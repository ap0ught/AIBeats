"""l53b: prefix rows + legalized TAS rows (TAS frames TJ+1..T1, shifted) + tail rows, from a start state; report events and
divergence from the TAS. python work/l53b/chain.py <mst|tasF> F0 --pre file|'' --tj TJ --t1 T1 [--tail file] [--hist file]
 [--poke 65=3,64=35] [--out file] [--every 25] [--pad 0] [--ov 'f-f=Row;...' (TAS frames)]"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
PRE = opt('--pre', ''); TJ = opt('--tj', 0); T1 = opt('--t1', 0); TAIL = opt('--tail', ''); HIST = opt('--hist', '')
POKE = opt('--poke', ''); OUT = opt('--out', ''); EV = opt('--every', 25); PAD = opt('--pad', 0); OV = opt('--ov', '')
src, F0 = a[0], int(a[1])
def rd(p): return [row(l.strip()) for l in open(p) if l.strip() and not l.startswith('#')]
ov = {}
for part in [p for p in OV.split(';') if p]:
    k, v = part.split('='); x, y = (map(int, k.split('-')) if '-' in k else (int(k), int(k)))
    for f in range(x, y + 1): ov[f] = set(row(v))
hist = rd(HIST) if HIST else [()] * 150
rows = rd(PRE) if PRE else []
en = A.Enforcer(hist + rows)
def want(f):
    if f in ov: return tuple(sorted(ov[f]))
    w = set(T(f))
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    return tuple(sorted(w))
nj = len(rows)
for f in range(TJ + 1, T1 + 1): rows.append(tuple(sorted(en.emit(want(f)))))
nt = len(rows)
if TAIL: rows += rd(TAIL)
print('legal:', legal_ok(rows, hist) or 'ok', 'rows', len(rows), 'last frame', F0 + len(rows))
fc = core(src) if src.endswith('.mst') else core_at(F0)
for p in [q for q in POKE.split(',') if q]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
fc.save('b'); fc._ka_slot = 'b'
st = fc.run_batch('b', [rows + [()] * PAD], record='all')[0].states
fc.close()
L = F0 + nj - TJ
prev = None; first = None
for i, s in enumerate(st):
    f = F0 + 1 + i; X, y = RXY(s); ev = []
    if nj <= i < nt:
        tf_ = f - L
        if (X, y) != tas_xy(tf_) and first is None: first = f; ev.append(f'DIVERGE from TAS {tf_} {tas_xy(tf_)}')
    if prev:
        for k in ('hp65', 'np64', 'item', 'room6e'):
            if s[k] != prev[k]: ev.append(f'{k} {prev[k]}->{s[k]}')
    if ev or (EV and i % EV == 0) or i == len(st) - 1:
        print(f, P(rows[i]) if i < len(rows) else '(pad)', f'X {X} y {y} hp {s["hp65"]} np {s["np64"]} rm {s["room6e"]} TASeq {f - L}', ' '.join(ev))
    prev = s
print('lag', L, 'first diverge', first)
if OUT:
    with open(OUT, 'w') as fo:
        fo.write(f'# l53b chain from {src} F0 {F0}: pre {PRE}, TAS {TJ+1}..{T1} at lag {L}, tail {TAIL}\n')
        for r in rows: fo.write(P(r) + '\n')
