"""NesHawk arrival scan: ref state + TAS rows to F0, then rows file (from F0+1) with ADDR poked to each value.
Compares every frame's (X, y, hp, room) with the unpoked run; prints classes (first divergence frame, end hp/np/room, goal frame).
python work/l63p/nhbf.py <refstate> F0 rowsfile [--addr 0xBF] [--vals 0-255] [--pre a=v,..] [--goal 'rm==42']"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l63p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
from lib0 import XY
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
AD = int(opt('--addr', '0xBF'), 0); VS = opt('--vals', '0-255'); PRE = opt('--pre', ''); GOAL = opt('--goal', '')
stn, F0, RF = a[0], int(a[1]), a[2]
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
rows = [row(l.strip()) for l in open(RF) if not l.startswith('#')]
if '-' in VS and ',' not in VS:
    st_ = 1
    if ':' in VS: VS, st_ = VS.split(':'); st_ = int(st_)
    x, y = map(int, VS.split('-')); vals = list(range(x, y + 1, st_))
else: vals = [int(v) for v in VS.split(',')]
TR = A.tas_rows()
G = compile(GOAL, 'g', 'eval') if GOAL else None
e = C.open_emu('l63p_nhbf.log')
def sig(m): return (XY(m), m[0x65], m[0x6E], m[0x64], m[0xC9], m[0x66])
try:
    e.tick(TICKS)
    st = e.load(stn); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, F0 + 1)])
    for kv in [p for p in PRE.split(',') if p]:
        k_, v_ = kv.split('='); e.poke(int(k_, 0), int(v_, 0))
    base = e.msave()
    _, ref = e.run_ram(rows); orig = None
    e.mload(base)
    import struct
    groups = {}
    for v in vals:
        e.mload(base); e.poke(AD, v)
        _, rams = e.run_ram(rows)
        div = next((F0 + 1 + i for i, (m, r) in enumerate(zip(rams, ref)) if sig(m) != sig(r)), None)
        d0 = next((i for i, (m, r) in enumerate(zip(rams, ref)) if m[0x400:0x4A8] != r[0x400:0x4A8]), None)
        who = ''
        if d0 is not None:
            m, r = rams[d0], ref[d0]
            sl = sorted({(ad - 0x400) % 8 for ad in range(0x400, 0x4A8) if m[ad] != r[ad]})
            who = f'slots@{F0 + 1 + d0}: ' + ','.join(f's{j}t{r[0x400 + j]}({r[0x460 + j]},{r[0x480 + j]})' for j in sl)
        gf = None
        if G:
            for i, m in enumerate(rams):
                X, y = XY(m)
                if eval(G, dict(X=X, y=y, hp=m[0x65], rm=m[0x6E], np=m[0x64], it=m[0xC9], boss=m[0x66], m=m)): gf = F0 + 1 + i; break
        m = rams[-1]
        k = (div is None, gf, m[0x65], m[0x64], m[0x6E])
        groups.setdefault(k, []).append((v, div))
        print(v, 'div', div, 'goal', gf, 'end hp', m[0x65], 'np', m[0x64], 'rm', m[0x6E], who, flush=True)
finally:
    e.close()
print('== classes (same-as-ref, goal frame, hp, np, room): values')
for k, vs in sorted(groups.items(), key=lambda q: -len(q[1])): print(k, len(vs), [v for v, _ in vs])
