"""Local legal beam on the TAS 4-2 line with a $BF poke (Mesen).
python -u work/l42p/beam42.py <bf@control> <win 1|2> [--width 24] [--frames 220] [--hpw 6] [--tag t]
win 1 (tosser 1): poke at control 16,682, TAS pads to 17,030, beam until X >= 760 (TAS 17,145).
win 2 (tossers 2/3): TAS pads to 17,355 (bf unpoked), poke $BF = (bf + 673) & 255 there (= bf's value at 17,355 on TAS
pace), TAS pads to 17,440, beam until X >= 1,450 (TAS 17,605).
Score: |X - X_tas(f)| + 0.3 |y - y_tas(f)| + hpw * hp lost. Reports every goal node: (frame - TAS frame at goal X, hp, np)."""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
BTN = ('A', 'B', 'Left', 'Right', 'Up', 'Down')
class Leg:
    """per-button legality: new press >= 5 f after the previous press, hold >= 2, release >= 2"""
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
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
W = opt('--width', 40); NF = opt('--frames', 220); HPW = opt('--hpw', 6.0); TAG = opt('--tag', ''); DBG = opt('--dbg', 0)
ALPHA = opt('--alpha', 'Right|A+Right|B+Right|Down+B+Right|-')
BFS, win = [int(v) for v in a[0].split(',')], int(a[1])
d = open('work/l42p/tas42_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
def tm(f): i = f - f0 - 1; return d[i*2048:(i+1)*2048]
def tX(f): m = tm(f); return m[0x52]*256 + m[0x51] + m[0x86]
R2D = C.rows_of('logs/a34/4-2_r2d.inputs.txt')
FL = {'x': 0x86, 'xsub': 0x85, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'vy': 0x89, 'vys': 0x87, 'coll': 0x8C, 'anim': 0x80,
      'hp': 0x65, 'np': 0x64, 'it': 0xC9, 'st': 0x6D, 'en': 0x73}
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open('states/mesen/l42p_tas16682.mst', 'rb').read()); fc._ka_slot = 's'
for bf in BFS:
    fc.load('s'); fc._ka_slot = 's'
    if win == 1: S, XG, PK, PF = 17030, 760, bf, 16682
    elif win == 2: S, XG, PK, PF = 17440, 1450, (bf + 673) & 255, 17355
    else: S, XG, PK, PF = 17440, 1450, bf, 16682   # win 3 = window 2 with the poke at control (= the real chain for c = bf)
    TG = next(f for f in range(f0 + 1, f0 + len(d)//2048) if tX(f) >= XG)
    if PF == 16682:
        fc.poke(0xBF, PK); fc.step(pads[:S - 16682], record='last')
    else:
        fc.step(pads[:PF - 16682], record='last'); fc.poke(0xBF, PK); fc.step(pads[PF - 16682:S - 16682], record='last')
    fc.save('s0'); fc._ka_slot = 's0'
    r0 = fc.ram(); HP0 = r0[0x65]
    hist = [()] * 1500 + R2D[:S - 16681]
    def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
    AL = [row(x) for x in ALPHA.split('|')]
    def X(s): return s['sh']*256 + s['sl'] + s['x']
    def score(s, f):
        m = tm(f); return abs(X(s) + s['xsub']/256 - tX(f)) + 0.3*abs(s['y'] - m[0x8A]) + HPW*(HP0 - s['hp'])
    nodes = [('s0', (), Leg(hist), None)]
    goals = []; t0 = time.time()
    for fr in range(NF):
        f = S + fr + 1
        out = []
        for ni, (slot, rows, en, s) in enumerate(nodes):
            kids = {}
            for w in AL:
                e2 = en.copy(); lg = tuple(sorted(e2.emit(w)))
                if lg not in kids: kids[lg] = e2
            kl = list(kids.items())
            rr = fc.run_batch(slot, [[lg] for lg, _ in kl], record='last', keep=True, prefix=f'g{fr}n{ni}_')
            for (lg, e2), r in zip(kl, rr):
                if not r.states: continue
                st = r.states[-1]
                out.append((r.slot, rows + (lg,), e2, st))
        if fr: fc.drop_prefix(f'g{fr-1}n')
        nxt = []; seen = set()
        for n in sorted(out, key=lambda n: score(n[3], f)):
            s = n[3]
            if s['hp'] == 0 or s['st'] != 9: continue
            if X(s) >= XG:
                goals.append((f - TG, s['hp'], s['np'], n[1])); continue
            k = (X(s), s['xsub'], s['y'], s['vy'], s['vys'], s['coll'], s['anim'], s['hp'], s['np'], s['en'], tuple(sorted((b, v[0], min(v[1], 2), max(-1, min(5, n[2].f - v[2]))) for b, v in n[2].st.items())))
            if k in seen: continue
            seen.add(k); nxt.append(n)
            if len(nxt) >= W: break
        nodes = nxt
        if DBG == 2:
            for n in nodes[:30]: print(f, X(n[3]), n[3]['y'], n[3]['anim'], n[3]['hp'], round(score(n[3], f), 1), n[1])
        if DBG and fr % 10 == 0 and nodes:
            b = nodes[0][3]; print(f, 'best X', X(b), 'y', b['y'], 'hp', b['hp'], 'np', b['np'], 'tasX', tX(f), 'rows', nodes[0][1][-6:], flush=True)
        if goals and f - TG > 12: break
        if not nodes: break
    best = {}
    for lag, hp, np_, rows in goals:
        k = (hp, np_)
        if k not in best or lag < best[k][0]: best[k] = (lag, rows)
    print(f'bf {bf} win {win} poke {PK}@{PF} goalX {XG} TAS {TG}  results (hp,np)->lag:',
          sorted(((k, v[0]) for k, v in best.items()), key=lambda q: q[1]), f'{time.time()-t0:.0f}s', flush=True)
    if best and TAG:
        k = min(best, key=lambda q: (best[q][0], -q[0]))
        C.write_inputs(f'work/l42p/bm_{TAG}{bf}.inputs.txt', R2D[:S - 16681] + list(best[k][1]), f'beam42 bf {bf} win {win} best {k} lag {best[k][0]}')

    fc.drop_prefix('g')
fc.close()
