"""NesHawk: base = legalized TAS rows F0+1..F1 (+tail), variants = override specs (one per line in a file or '|'-separated);
reports per variant: first hp loss, end hp/np/item, first frame the goal holds. python work/l63p/nhgrid.py <ref> F0 F1 'goal' 'v1|v2' [--tail R --n N --poke ..]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l63p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
import a34_core as K
from lib0 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
TAIL = opt('--tail', 'Right'); JS = opt('--js', 0); N = opt('--n', 0); PK = opt('--poke', '')
stn, F0, F1, GOAL, VS = a[0], int(a[1]), int(a[2]), a[3], a[4]
TR = A.tas_rows()
def T(f): return set(TR[f - 1]) if f - 1 < len(TR) else set()
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
def parse(OV):
    ov = {}
    for part in [p for p in OV.split(';') if p]:
        k, v = part.split('=')
        x, y = (map(int, k.split('-')) if '-' in k else (int(k), int(k)))
        for f in range(x, y + 1): ov[f] = set(row(v))
    return ov
def want(f, ov):
    if f in ov: return ov[f]
    if f > F1: return set(row(TAIL))
    w = T(f)
    if JS and 'B' in w and 'Down' not in w and (TM(f - 1)[0x84] & 4): w = (w - {'Up'}) | {'Down'}
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    return w
hist = [tuple(sorted(want(f, {}))) for f in range(F0 - 150, F0 + 1)]
G = compile(GOAL, 'g', 'eval')
specs = open(VS[1:]).read().split('\n') if VS.startswith('@') else VS.split('|')
e = C.open_emu('l63p_nhgrid.log')
try:
    e.tick(TICKS)
    st = e.load(stn); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, F0 + 1)])
    for kv in [p for p in PK.split(',') if p]:
        k_, v_ = kv.split('='); e.poke(int(k_, 0), int(v_, 0))
    base = e.msave()
    for sp in specs:
        ov = parse(sp)
        en = A.Enforcer(hist); rows = [tuple(sorted(en.emit(tuple(sorted(want(f, ov)))))) for f in range(F0 + 1, max(F1, F0 + N) + 1)]
        L = K.Legal(hist[-1900:]); bad = ''
        for i, r in enumerate(rows):
            w = L.why(tuple(r))
            if w: bad = f'{i}:{w}'; break
            L.push(tuple(r))
        e.mload(base)
        _, rams = e.run_ram(rows)
        hp0 = rams[0][0x65]; hit = next((F0 + 1 + i for i, m in enumerate(rams) if m[0x65] < hp0), None)
        gf = None
        for i, m in enumerate(rams):
            X, y = XY(m)
            if eval(G, dict(X=X, y=y, hp=m[0x65], rm=m[0x6E], np=m[0x64], it=m[0xC9], m=m)): gf = F0 + 1 + i; break
        m = rams[-1]
        print(f'{sp:40s} legal {bad or "ok"} hit {hit} goal {gf} end hp {m[0x65]} np {m[0x64]} it {m[0xC9]} XY {XY(m)}', flush=True)
finally:
    e.close()
