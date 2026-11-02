"""l62: NesHawk 6-5 tries. From state ST (saved on/after the 6-4b kill K2, before the Start), for each delay d: Start on S3+d (S3 = earliest),
control C3+d, demon line (pick for bf+d, or --line), report kill / P / E / END seen / deaths.
python work/l62/nhdemon.py ST K2 S3 C3 bf0 t62 e3e d1,d2,... [--line file] [--all]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l65')
from ng.solve import common as C
from ng.mode import TICKS
import pick
a = sys.argv[1:]
LINE = None; ALL = '--all' in a
if ALL: a.remove('--all')
if '--line' in a: i = a.index('--line'); LINE = a[i+1]; del a[i:i+2]
ST, K2, S3, C3, bf0, t62, e3e = a[0], *map(int, a[1:7]); DS = [int(x) for x in a[7].split(',')]
def rf(p):
    L = open(p).read().split(chr(10))
    if L and L[-1] == '': L = L[:-1]
    return [() if l.strip() in ('', '-') else tuple(sorted(l.strip().split('+'))) for l in L if not l.startswith('#')]
tab = pick.load()
e = C.open_emu('l62_nhdemon.log')
try:
    e.tick(TICKS); st = e.load(ST); f0 = st['frame']; base = e.msave()
    for d in DS:
        e.mload(base)
        _, rr0 = e.run_ram([()] * (S3 + d - f0 - 1) + [('Start',), ('Start',)] + [()] * 170)
        ld = next(f0 + 1 + i for i, r in enumerate(rr0) if r[0x6D] == 21)
        C3x = ld + 152; m1 = rr0[C3x - 1 - f0 - 1]; bfx, t62x, e3ex = m1[0xBF], m1[0x62], m1[0x3E]
        cands = [(None, LINE)] if LINE else [(c[0], c[3]) for c in (pick.best(bfx, t62x, e3ex, tab) or [])][: (99 if ALL else 1)]
        if not cands: print('d', d, 'load', ld, 'ctl', C3x, 'bf', bfx, 'NO LINE', flush=True)
        for eo, line in cands:
            if line is None: print('d', d, 'bf', bf0 + d, 'no line'); continue
            e.mload(base)
            w = [()] * (S3 + d - f0 - 1) + [('Start',), ('Start',)] + [()] * (C3x - 1 - (S3 + d + 1)) + rf(line) + [()] * 700
            _, rr = e.run_ram(w)
            fK = f0 + 1; c3 = C3x
            K3 = next((fK + i for i, r in enumerate(rr) if fK + i >= c3 and r[0x6D] == 21 and r[0x66] == 0), None)
            P = next((fK + i for i, r in enumerate(rr) if K3 and fK + i > K3 and r[0x6D] == 21 and r[0x63] == 0), None)
            E = next((fK + i for i, r in enumerate(rr) if P and fK + i > P and r[0x3E] == 1), None)
            dead = next((fK + i for i, r in enumerate(rr) if r[0x6E] == 35), None)
            bfc = rr[c3 - 1 - fK][0xBF]
            print(f'd {d} load {ld} ctl {c3} t62 {t62x} e3e {e3ex} bf@ctl-1 {bfc} line {line} pred {eo} | kill {K3} (ctl+{K3 - c3 if K3 else None}) P {P} END seen {E + 1 if E else None} '
                  f'(ctl+{E + 1 - c3 if E else None}) death {dead} hp {min(r[0x65] for r in rr[c3 - fK:]) }', flush=True)
finally:
    e.close()
