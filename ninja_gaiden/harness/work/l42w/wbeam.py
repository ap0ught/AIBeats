"""Exit-wall beam (4-2, Mesen): from a state, frame-by-frame legal rows until the stage-end trigger ($5C 2 -> 0).
python -u work/l42w/wbeam.py <mst> <start frame> [--hist rows.txt] [--prefix rows.txt] [--width 150] [--frames 110]
       [--hpw 4] [--npmin 10] [--tag t] [--alpha 'Right|A+Right|...'] [--dbg 1]
--hist: the rows BEFORE the state (power-on or stage rows, only the tail matters) for per-button legality.
--prefix: rows played from the state before the beam starts (also judged for legality via hist+prefix).
Score: h = max(0, 3035 - X)/1.5 + max(0, y - 84)/1.8  + hpw * hp lost (lower = better). Goal: $5C == 0 (trigger).
Prints each goal (trigger frame, hp, np) and writes work/l42w/wb_<tag>.inputs.txt = prefix + beam rows (best: earliest,
then most hp)."""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
BTN = ('A', 'B', 'Left', 'Right', 'Up', 'Down')
class Leg:
    def __init__(self, hist):
        self.f = 0; self.st = {}
        for b in BTN:
            held = False; run = 99; lp = -99
            for i, r in enumerate(hist):
                h = b in r
                if h and not held: lp = i
                run = run + 1 if h == held else 1
                held = h
            self.st[b] = (held, run, lp - len(hist))
    def copy(self):
        c = Leg.__new__(Leg); c.f = self.f; c.st = dict(self.st); return c
    def emit(self, w):
        out = []
        for b in BTN:
            held, run, lp = self.st[b]
            want = b in w
            if held: h = True if run < 2 else want
            else: h = want and run >= 2 and self.f - lp >= 5
            if h and not held: lp = self.f
            run = run + 1 if h == held else 1
            self.st[b] = (h, run, lp)
            if h: out.append(b)
        self.f += 1
        return tuple(out)
    def key(self):
        return tuple(sorted((b, v[0], min(v[1], 2), max(-1, min(5, self.f - v[2]))) for b, v in self.st.items()))
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
W = opt('--width', 150); NF = opt('--frames', 110); HPW = opt('--hpw', 4.0); TAG = opt('--tag', ''); DBG = opt('--dbg', 0)
NPMIN = opt('--npmin', 10); GOALX = opt('--goalx', 0); ALIVE = opt('--alive', -1); ALIVEX = opt('--alivex', 99999); HPMIN = opt('--hpmin', 0); NPGOAL = opt('--npgoal', 0); CONTACT = opt('--contact', 0); BOUND = opt('--bound', 0); BR = opt('--br', 3.0); XW = opt('--xw', 3030); YS = opt('--ys', 1.8); VYW = opt('--vyw', 0.0); HIST = opt('--hist', ''); PRE = opt('--prefix', ''); NG = opt('--ngoals', 6)
ALPHA = opt('--alpha', 'Right|A+Right|Right+Up|A+Right+Up|Left|A+Left|A+Left+Up|Left+Up|-|A|Up|A+Up|Down+B+Right|Down+B+Left')
MST, F0 = a[0], int(a[1])
FL = {'x': 0x86, 'xsub': 0x85, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'vy': 0x89, 'vys': 0x87, 'coll': 0x8C, 'anim': 0x80,
      'hp': 0x65, 'np': 0x64, 'it': 0xC9, 'st': 0x6D, 'en': 0x73, 'c5': 0x5C, 'inv': 0x95, 'rf': 0x84}
for i in range(8):
    FL[f't{i}'] = 0x400 + i; FL[f'ex{i}'] = 0x460 + i; FL[f'ey{i}'] = 0x480 + i; FL[f'al{i}'] = 0x410 + i
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(MST, 'rb').read()); fc._ka_slot = 's'; fc.load('s')
hist = [tuple(r) for r in C.rows_of(HIST)] if HIST else [()] * 30
PR = [tuple(r) for r in C.rows_of(PRE)] if PRE else []
if PR:
    fc.step(PR, record='last')
fc.save('s0'); fc._ka_slot = 's0'
r0 = fc.ram(); HP0 = r0[0x65]
S = F0 + len(PR)
print('start', S, 'X', r0[0x52]*256 + r0[0x51] + r0[0x86], 'y', r0[0x8A], 'hp', HP0, 'np', r0[0x64], 'it', r0[0xC9], 'BF', r0[0xBF], flush=True)
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
AL = [row(x) for x in ALPHA.split('|')]
def X(s): return s['sh']*256 + s['sl'] + s['x']
def score(s):
    if GOALX: return -(X(s) + s['xsub']/256)/1.5 + HPW*(HP0 - s['hp']) + 0.02*s['y']
    return max(0, XW - X(s) - s['xsub']/256)/1.5 + max(0, s['y'] + VYW*(s['vy'] - 256 if s['vy'] > 127 else s['vy']) - 84)/YS + HPW*(HP0 - s['hp'])
nodes = [('s0', (), Leg(hist + PR), None)]
goals = []; t0 = time.time()
for fr in range(NF):
    f = S + fr + 1
    out = []
    for ni, (slot, rows, en, s) in enumerate(nodes):
        kids = {}
        for w in AL:
            e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
            if ('Left' in lg and 'Right' in lg) or ('Up' in lg and 'Down' in lg): continue
            if lg not in kids: kids[lg] = e2
        kl = list(kids.items())
        rr = fc.run_batch(slot, [[lg] for lg, _ in kl], record='last', keep=True, prefix=f'g{fr}n{ni}_')
        for (lg, e2), r in zip(kl, rr):
            if not r.states: continue
            out.append((r.slot, rows + (lg,), e2, r.states[-1]))
    if fr: fc.drop_prefix(f'g{fr-1}n')
    nxt = []; seen = set()
    for n in sorted(out, key=lambda n: score(n[3])):
        s = n[3]
        if s['hp'] == 0 or s['st'] != 9 or s['it'] != 133 or s['np'] < NPMIN: continue
        if s['hp'] < HPMIN: continue
        if ALIVE >= 0 and X(s) < ALIVEX and not (s[f't{ALIVE}'] == 11 and s[f'al{ALIVE}']): continue
        if GOALX and X(s) >= GOALX and s['np'] >= NPGOAL:
            goals.append((f, s['hp'], s['np'], n[1])); continue
        if s['c5'] == 0 or (CONTACT and X(s) >= 3030 and (s['coll'] == 32 or s['anim'] in (10, 12))):
            goals.append((f + (0 if s['c5'] == 0 else max(0, s['y'] - 84) / 1.8), s['hp'], s['np'], n[1])); continue
        if BOUND and f + max(0, s['y'] - 84) / BR > BOUND: continue
        k = (X(s), s['xsub'], s['y'], s['vy'], s['vys'], s['coll'], s['anim'], s['hp'], s['np'], s['inv'], s['rf'],
             tuple((s[f't{i}'], s[f'ex{i}'], s[f'ey{i}']) for i in range(8)), n[2].key())
        if k in seen: continue
        seen.add(k); nxt.append(n)
        if len(nxt) >= W: break
    if not nxt and nodes and TAG:
        C.write_inputs(f'work/l42w/wb_{TAG}_last.inputs.txt', PR + list(nodes[0][1]), f'wbeam {MST} last surviving node at {f - 1}')
    nodes = nxt
    if DBG and nodes:
        b = nodes[0][3]
        print(f, 'n', len(nodes), 'best X', X(b), 'y', b['y'], 'hp', b['hp'], 'anim', b['anim'], 'coll', b['coll'], 'sc', round(score(b), 1), 'rows', nodes[0][1][-5:], flush=True)
    if len(goals) >= NG or (goals and f - goals[0][0] > 6): break
    if not nodes: break
best = {}
for g, hp, np_, rows in goals:
    if hp not in best or g < best[hp][0]: best[hp] = (g, rows)
print('goals (frame,hp,np):', sorted(set((round(g[0],1), g[1], g[2]) for g in goals))[:12]); print(f'from {S}: trigger by hp:', sorted(((k, v[0]) for k, v in best.items()), key=lambda q: (q[1][0] if False else q[1], -q[0])), f'{time.time()-t0:.0f}s', flush=True)
if best and TAG:
    k = min(best, key=lambda q: (best[q][0], -q))
    C.write_inputs(f'work/l42w/wb_{TAG}.inputs.txt', PR + list(best[k][1]), f'wbeam {MST} from {F0} trigger {best[k][0]} hp {k}')
    for hp in best:
        C.write_inputs(f'work/l42w/wb_{TAG}_h{hp}.inputs.txt', PR + list(best[hp][1]), f'wbeam {MST} from {F0} trigger {best[hp][0]} hp {hp}')
fc.drop_prefix('g'); fc.close()
