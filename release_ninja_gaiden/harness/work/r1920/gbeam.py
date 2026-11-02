"""Generic legal beam for room segments (agent r1920, Mesen).
python -u work/r1920/gbeam.py <mst> <start frame> --goal "<expr>" --h "<expr>" [--hist rows] [--prefix rows]
     [--width 200] [--frames 120] [--cell 4] [--cap 3] [--hpw 3] [--npmin 0] [--tag t] [--alpha 'R|AR|...']
     [--ngoals 8] [--keep "<expr>"] [--dbg 1]
Expressions see s (state dict), X (world X of s), f (frame), hp0, np0. --goal: node is a goal; --h: estimated frames
to go (lower = better; hp loss adds hpw per HP); --keep: prune nodes where it is False.
Writes work/r1920/gb_<tag>.inputs.txt (prefix + rows of the best goal: lowest --rank (default 0), then earliest)."""
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


AB = {'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B'}


def row(sp):
    return () if sp in ('-', '') else tuple(sorted(AB[c] for c in sp))


FL = {'x': 0x86, 'xsub': 0x85, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'vy': 0x89, 'vys': 0x87, 'coll': 0x8C, 'anim': 0x80,
      'hp': 0x65, 'np': 0x64, 'it': 0xC9, 'st': 0x6D, 'en': 0x73, 'c5': 0x5C, 'inv': 0x95, 'rf': 0x84, 'room': 0x6E,
      'bf': 0xBF}
for _i in range(8):
    FL[f't{_i}'] = 0x400 + _i; FL[f'ex{_i}'] = 0x460 + _i; FL[f'ey{_i}'] = 0x480 + _i


def X(s):
    h = s['sh'] - 256 if s['sh'] >= 128 else s['sh']
    return h * 256 + s['sl'] + s['x']


def main():
    a = sys.argv[1:]

    def opt(n, d):
        if n in a:
            i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
        return d
    W = opt('--width', 200); NF = opt('--frames', 120); HPW = opt('--hpw', 3.0); TAG = opt('--tag', '')
    DBG = opt('--dbg', 0); NPMIN = opt('--npmin', 0); CELL = opt('--cell', 4); CAP = opt('--cap', 3)
    HIST = opt('--hist', ''); PRE = opt('--prefix', ''); NG = opt('--ngoals', 8); GOAL = opt('--goal', 'False')
    HX = opt('--h', '0'); KEEP = opt('--keep', 'True'); RANK = opt('--rank', '0'); HPMIN = opt('--hpmin', 1)
    ALPHA = opt('--alpha', 'R|AR|L|AL|-|A|BR|BL|B|ABR|ABL')
    SLACK = opt('--slack', 4)
    MST, F0 = a[0], int(a[1])
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
    fc.put('s', open(MST, 'rb').read()); fc._ka_slot = 's'; fc.load('s')
    hist = [tuple(r) for r in C.rows_of(HIST)][-400:] if HIST else [()] * 30
    PR = [tuple(r) for r in C.rows_of(PRE)] if PRE else []
    if PR:
        fc.step(PR, record='last')
    fc.save('s0'); fc._ka_slot = 's0'
    r0 = fc.ram(); hp0 = r0[0x65]; np0 = r0[0x64]; st0 = r0[0x6D]; it0 = r0[0xC9]
    S = F0 + len(PR)
    sh = r0[0x52] - 256 if r0[0x52] >= 128 else r0[0x52]
    print('start', S, 'X', sh * 256 + r0[0x51] + r0[0x86], 'y', r0[0x8A], 'hp', hp0, 'np', np0, 'it', r0[0xC9], 'BF',
          r0[0xBF], flush=True)
    sys.path.insert(0, 'work/l43p')
    from lib import TM, XY

    def TX(t):
        m = TM(t); return XY(m)[0] if m else 0

    def TY(t):
        m = TM(t); return XY(m)[1] if m else 0
    _TPC = {}

    def TP(x_, y_, t1, t2, wy=0.5):
        """TAS-path progress: (TAS frame in [t1, t2] nearest to (x_, y_) in the room of t1, distance)"""
        if (t1, t2) not in _TPC:
            rm = TM(t1)[0x6E]
            _TPC[(t1, t2)] = [(t,) + XY(TM(t)) for t in range(t1, t2 + 1) if TM(t)[0x6E] == rm]
        bt, bd = t1, 1e9
        for t, x2, y2 in _TPC[(t1, t2)]:
            d = abs(x_ - x2) + wy * abs(y_ - y2)
            if d < bd: bd, bt = d, t
        return bt, bd
    env = {'X': X, 'TX': TX, 'TY': TY, 'TP': TP, 'abs': abs, 'max': max, 'min': min}
    fgoal = eval('lambda s, f, hp0, np0: ' + GOAL, env)
    fh = eval('lambda s, f, hp0, np0: ' + HX, env)
    fkeep = eval('lambda s, f, hp0, np0: ' + KEEP, env)
    frank = eval('lambda s, f, hp0, np0: ' + RANK, env)
    AL = [row(x) for x in ALPHA.split('|')]

    def score(s, f):
        return fh(s, f, hp0, np0) + HPW * (hp0 - s['hp'])
    nodes = [('s0', (), Leg(hist + PR), None)]
    goals = []; t0 = time.time(); lastbest = None
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
        if fr: fc.drop_prefix(f'g{fr - 1}n')
        nxt = []; seen = set(); cells = {}
        for n in sorted(out, key=lambda n: score(n[3], f)):
            s = n[3]
            if s['hp'] < HPMIN or s['st'] != st0 or s['np'] < NPMIN or s['it'] != it0: continue
            if not fkeep(s, f, hp0, np0): continue
            if fgoal(s, f, hp0, np0):
                goals.append((f, frank(s, f, hp0, np0), s['hp'], s['np'], n[1], X(s), s['y'])); continue
            k = (X(s), s['xsub'], s['y'], s['vy'], s['vys'], s['coll'], s['anim'], s['hp'], s['np'], s['inv'], s['rf'],
                 tuple((s[f't{i}'], s[f'ex{i}'], s[f'ey{i}']) for i in range(8)), n[2].key())
            if k in seen: continue
            seen.add(k)
            ck = (X(s) // CELL, s['y'] // CELL, s['anim'], s['rf'] & 0x44, s['hp'])
            if cells.get(ck, 0) >= CAP: continue
            cells[ck] = cells.get(ck, 0) + 1
            nxt.append(n)
            if len(nxt) >= W: break
        if nxt: lastbest = (f, nxt[0][1])
        nodes = nxt
        if DBG and nodes:
            b = nodes[0][3]
            print(f, 'n', len(nodes), 'best X', X(b), 'y', b['y'], 'hp', b['hp'], 'np', b['np'], 'an', b['anim'], 'co',
                  b['coll'], 'sc', round(score(b, f), 1), f'{time.time() - t0:.0f}s', flush=True)
        if len(goals) >= NG or (goals and f - goals[0][0] >= SLACK): break
        if not nodes: break
    goals.sort(key=lambda g: (g[1], g[0], -g[2]))
    print('goals (frame, rank, hp, np, X, y):', [(g[0], round(g[1], 2), g[2], g[3], g[5], g[6]) for g in goals[:12]],
          f'{time.time() - t0:.0f}s', flush=True)
    if goals and TAG:
        g = goals[0]
        C.write_inputs(f'work/r1920/gb_{TAG}.inputs.txt', PR + list(g[4]),
                       f'gbeam {MST} from {F0}: goal at {g[0]} hp {g[2]} np {g[3]} X {g[5]} y {g[6]}')
        print('wrote', f'work/r1920/gb_{TAG}.inputs.txt')
    if not goals and TAG and lastbest:
        C.write_inputs(f'work/r1920/gb_{TAG}_last.inputs.txt', PR + list(lastbest[1]), f'gbeam {MST} from {F0}: best node at {lastbest[0]} (no goal)')
    fc.drop_prefix('g'); fc.close()


if __name__ == '__main__':
    main()
