"""Frame-level legal beam/BFS on Mesen (wall agent, 2-1 lock round).
    python -u work/w21/fbfs.py <mst> <hist rows file|-> <goal> <out rows file> [--depth 200] [--cap 3000]
        [--buttons A,L,R] [--score y|x+|x-|wp:X1:Y1,X2:Y2..] [--bucket 2] [--per 2] [--minhp 0] [--npmin 0]
goal: room:N | stage | x:ge|le:GX[:ylo:yhi] (+room implicit: current) | land:X0:X1:Y (standing coll!=0 y==Y)
Every frame, every legal row from the button set (exact rules: press period 5, hold >= 2, release >= 2, no L+R/U+D;
the 600/1800 windows are checked at the end) is tried from every frontier state. States are deduplicated by Ryu's
physics + room + a legality signature; the frontier is pruned to --cap by score with per-bucket diversity.
Writes the rows of the earliest goal (only the new rows). Mesen only: candidates must be verified on NesHawk."""
import sys, time, threading, itertools
sys.path.insert(0, '.')
from ng.solve import common as C
from ng import fastcore as F

a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
DEPTH = opt('--depth', 200); CAP = opt('--cap', 3000); BTN = [{'A':'A','B':'B','L':'Left','R':'Right','U':'Up','D':'Down'}.get(b,b) for b in opt('--buttons', 'A,L,R').split(',')]
SCORE = opt('--score', 'y'); BK = opt('--bucket', 2); PER = opt('--per', 2); MINHP = opt('--minhp', 0)
NPMIN = opt('--npmin', 0); NW = opt('--workers', 2); KEEP = opt('--keep', 0)
mst, histf, goal, outf = a[:4]
hist = C.rows_of(histf) if histf != '-' else []
G = goal.split(':')
OPPS = {'Left': 'Right', 'Right': 'Left', 'Up': 'Down', 'Down': 'Up'}

# ---- legality signature per button: (held, run capped 5, since-start capped 5)
def sig0(hist):
    s = {}
    for b in BTN:
        held = False; run = 9; since = 9
        for r in hist[-12:]:
            h = b in r
            since = min(9, since + 1)
            if h and not held: held = True; run = 1; since = 1
            elif h: run = min(9, run + 1)
            elif held: held = False; run = 1
            else: run = min(9, run + 1)
        s[b] = (held, run, since)
    return s

def legal_rows(s):
    """all rows (tuples of buttons) legal after signature s"""
    opts = []
    for b in BTN:
        held, run, since = s[b]
        can_on = held or (since >= 5 and run >= 2)
        can_off = (not held) or run >= 2
        o = []
        if can_off: o.append(False)
        if can_on: o.append(True)
        opts.append(o)
    out = []
    for combo in itertools.product(*opts):
        row = tuple(b for b, on in zip(BTN, combo) if on)
        if 'Left' in row and 'Right' in row: continue
        if 'Up' in row and 'Down' in row: continue
        out.append(row)
    return out

def step_sig(s, row):
    n = {}
    for b in BTN:
        held, run, since = s[b]
        h = b in row
        since = min(9, since + 1)
        if h and not held: n[b] = (True, 1, 1)
        elif h: n[b] = (True, min(9, run + 1), since)
        elif held: n[b] = (False, 1, since)
        else: n[b] = (False, min(9, run + 1), since)
    return n

def sigkey(s):
    # collapse values that no longer matter (run>=2 / since>=5 behave the same)
    return tuple((h, min(r, 2), min(sn, 5)) for h, r, sn in (s[b] for b in BTN))

def phys(st):
    return (st['room'], st['x'], st['xsub'], st['y'], st['vy'], st['vy_sub'], st['coll'], st['anim'], st['rflags'],
            st['vx'], st['vx_sub'], st['scroll'], st['scroll_scr'], st['hp'], st['ninpo'])

def reached(st, room0, stage0):
    if G[0] == 'stage': return st['stage'] != stage0
    if G[0] == 'room': return st['room'] == int(G[1]) or st['stage'] != stage0
    X = C.abs_x(st)
    if G[0] == 'x':
        ok = X >= int(G[2]) if G[1] == 'ge' else X <= int(G[2])
        if ok and len(G) > 3: ok = int(G[3]) <= st['y'] <= int(G[4])
        return ok and st['room'] == room0
    if G[0] == 'land':
        return int(G[1]) <= X <= int(G[2]) and st['y'] == int(G[3]) and not (st['rflags'] & 4)
    raise ValueError(goal)

WP = None
if SCORE.startswith('wp:'):
    WP = [tuple(map(int, p.split(':'))) for p in SCORE[3:].split(',')]
def score(st):
    X, y = C.abs_x(st), st['y']
    if SCORE == 'y': return y + (0 if st['coll'] else 0)
    if SCORE == 'x+': return -X
    if SCORE == 'x-': return X
    if SCORE == 'xy+': return -X + y      # right and up
    if SCORE == 'xy-': return X + y       # left and up
    if WP:
        # distance to go along the waypoint chain from the nearest segment point ahead
        best = None
        for i in range(len(WP)):
            px, py = WP[i]
            d = abs(px - X) / 1.5 + abs(py - y) / 2.0
            rest = 0.0
            for j in range(i, len(WP) - 1):
                rest += abs(WP[j + 1][0] - WP[j][0]) / 1.5 + abs(WP[j + 1][1] - WP[j][1]) / 2.0
            v = d + rest
            if best is None or v < best: best = v
        return best
    raise ValueError(SCORE)

class Node:
    __slots__ = ('w', 'slot', 'sig', 'parent', 'row', 'st')
    def __init__(s, w, slot, sig, parent, row, st):
        s.w, s.slot, s.sig, s.parent, s.row, s.st = w, slot, sig, parent, row, st

def path(n):
    out = []
    while n is not None and n.row is not None:
        out.append(n.row); n = n.parent
    return out[::-1]

P = F.FastPool(NW, boot_rows=None, ticks=True)
data = open(mst, 'rb').read()
for w in P.workers: w.put('root', data); w.load('root')
_, rr, _ = P.workers[0].step([], record='last') if False else (0, None, 0)
st0 = P.workers[0].run_batch('root', [[()]], record='last')[0].states[-1]   # peek (one blank frame)
room0, stage0 = st0['room'], st0['stage']
print(f"start room {room0} stage {stage0} (peek after 1 blank: X {C.abs_x(st0)} y {st0['y']})", flush=True)
root = Node(0, 'root', sig0(hist), None, None, None)
P.workers[1 % NW].put('root', data)
frontier = [root]
uid = itertools.count()
t0 = time.time()
found = None
seen = set()
for depth in range(1, DEPTH + 1):
    # expand, per worker
    per = [[n for n in frontier if n.w == wi] for wi in range(NW)]
    children = []
    lock = threading.Lock()
    errs = []
    def work(wi):
        w = P.workers[wi]
        loc = []
        dr = []
        try:
            for n in per[wi]:
                rows = legal_rows(n.sig)
                pre = f"n{next(uid)}_"
                res = w.run_batch(n.slot, [[r] for r in rows], record='last', keep=True, prefix=pre)
                for r, rs in zip(rows, res):
                    if not rs.rows_played or not rs.states: continue
                    loc.append(Node(wi, rs.slot, step_sig(n.sig, r), n, r, rs.states[-1]))
                if n.slot != 'root': dr.append(n.slot)
            for i in range(0, len(dr), 20): w.drop(*dr[i:i+20])
        except Exception as e:
            errs.append(e)
        with lock:
            children.extend(loc)
    th = [threading.Thread(target=work, args=(wi,)) for wi in range(NW)]
    for t in th: t.start()
    for t in th: t.join()
    if errs: raise errs[0]
    # goal / death / dedup
    keep = []
    hits = []
    for c in children:
        st = c.st
        if st['hp'] == 0 or (st['dead'] & 0x80) or st['hp'] < MINHP or (st['y'] >= 0xF0 and st['room'] == room0 and False):
            continue
        if reached(st, room0, stage0) and st['ninpo'] >= NPMIN:
            hits.append(c); continue
        k = (phys(st), sigkey(c.sig))
        if k in seen: continue
        seen.add(k)
        keep.append(c)
    if hits:
        hits.sort(key=lambda c: (-c.st['hp'], -c.st['ninpo']))
        found = hits[0]
        print(f"GOAL at depth {depth}: X {C.abs_x(found.st)} y {found.st['y']} room {found.st['room']} hp {found.st['hp']} np {found.st['ninpo']}  ({len(hits)} hits)", flush=True)
        break
    # prune: buckets
    keep.sort(key=lambda c: score(c.st))
    bcount = {}
    nxt = []
    for c in keep:
        st = c.st
        b = (C.abs_x(st) // BK, st['y'] // BK, st['room'], bool(st['rflags'] & 4), st['coll'] != 0, st['vy'] >= 128)
        if bcount.get(b, 0) >= PER: continue
        bcount[b] = bcount.get(b, 0) + 1
        nxt.append(c)
        if len(nxt) >= CAP: break
    sel = set(id(c) for c in nxt)
    for wi in range(NW):
        dr = [c.slot for c in children if id(c) not in sel and c.slot and c.w == wi]
        for i in range(0, len(dr), 20): P.workers[wi].drop(*dr[i:i+20])
    frontier = nxt
    # rebalance workers
    if NW > 1 and frontier:
        cnt = [sum(1 for n in frontier if n.w == wi) for wi in range(NW)]
        while max(cnt) - min(cnt) > max(20, len(frontier) // 10):
            hi = cnt.index(max(cnt)); lo = cnt.index(min(cnt))
            n = next(n for n in frontier if n.w == hi)
            d = P.workers[hi].get(n.slot); P.workers[hi].drop(n.slot)
            P.workers[lo].put(n.slot, d); n.w = lo
            cnt[hi] -= 1; cnt[lo] += 1
    if not frontier:
        print('frontier empty at depth', depth); break
    b = frontier[0].st
    if True:
        print(f"d {depth} children {len(children)} uniq {len(keep)} kept {len(frontier)} best X {C.abs_x(b)} y {b['y']} "
              f"coll {b['coll']} score {score(b):.1f} {time.time()-t0:.0f}s", flush=True)
P.close()
if found:
    rows = path(found)
    C.write_inputs(outf, rows, f'fbfs {mst} goal {goal} depth {len(rows)}')
    print('wrote', outf, len(rows), 'rows')
