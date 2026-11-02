"""NesHawk: follow legalized TAS rows (or a rows file) from TAS frame F0 (ref state + TAS rows), compare with the TAS dump.
python work/l63p/nhtf.py <refstate> F0 F1 [--ov 'a-b=Row;..'] [--rows file] [--every k] [--tail Right --n N] [--poke a=v,..]"""
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
OV = opt('--ov', ''); RF = opt('--rows', ''); EV = opt('--every', 0); TAIL = opt('--tail', ''); N = opt('--n', 0); PK = opt('--poke', '')
OUT = opt('--out', ''); JS = opt('--js', 0); SH = opt('--shift', 0)
stn, F0, F1 = a[0], int(a[1]), int(a[2])
TR = A.tas_rows()
def T(f): return set(TR[f - 1]) if f - 1 < len(TR) else set()
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
ov = {}
for part in [p for p in OV.split(';') if p]:
    k, v = part.split('=')
    x, y = (map(int, k.split('-')) if '-' in k else (int(k), int(k)))
    for f in range(x, y + 1): ov[f] = set(row(v))
def want(f):
    if f in ov: return ov[f]
    if f > F1 and TAIL: return set(row(TAIL))
    w = T(f)
    if JS and 'B' in w and 'Down' not in w and (TM(f - 1)[0x84] & 4): w = (w - {'Up'}) | {'Down'}
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    return w
hist = [tuple(sorted(want(f))) for f in range(F0 - 150, F0 + 1)]
if RF: rows = [row(l.strip()) for l in open(RF) if not l.startswith('#')]
else:
    en = A.Enforcer(hist); rows = [tuple(sorted(en.emit(tuple(sorted(want(f)))))) for f in range(F0 + 1, max(F1, F0 + N) + 1)]
L = K.Legal(hist[-1900:]); bad = ''
for i, r in enumerate(rows):
    w = L.why(tuple(r))
    if w: bad = f'{i}:{w}'; break
    L.push(tuple(r))
print('legal:', bad or 'ok', 'rows', len(rows), flush=True)
e = C.open_emu('l63p_nhtf.log')
try:
    e.tick(TICKS)
    st = e.load(stn); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, F0 + 1)])
    for kv in [p for p in PK.split(',') if p]:
        k_, v_ = kv.split('='); e.poke(int(k_, 0), int(v_, 0))
    _, rams = e.run_ram(rows)
finally:
    e.close()
first = None; prev = None
for i, m in enumerate(rams):
    f = F0 + 1 + i; X, y = XY(m); t = TM(f - SH) if f - SH <= TF0 + NF else None; tX, ty = XY(t) if t else (None, None)
    ev = []
    if (X, y) != (tX, ty) and first is None: first = f; ev.append(f'FIRST DIVERGENCE (TAS {tX},{ty})')
    if prev:
        for nm, ad in (('hp', 0x65), ('np', 0x64), ('it', 0xC9), ('rm', 0x6E), ('st', 0x6D), ('boss', 0x66)):
            if m[ad] != prev[ad]: ev.append(f'{nm} {prev[ad]}->{m[ad]}')
    if ev or (EV and f % EV == 0):
        print(f, '+'.join(rows[i]) or '-', f'X {X} y {y} | TAS {tX},{ty} | hp {m[0x65]} np {m[0x64]} it {m[0xC9]} rm {m[0x6E]} BF {m[0xBF]}', ' '.join(ev))
    prev = m
if OUT: open(OUT, 'w').write('\n'.join('+'.join(r) or '-' for r in rows) + '\n')
