"""l53a: find where our rows (from 26608, TAS state 26607 + pokes) join the TAS at a lag L, then chain:
our rows to the join + legalized TAS rows (shifted by L) to TAS frame T1 + an optional tail rows file (rows from TAS T1+1).
python work/l53a/sync.py ours.txt [--tail file --t1 26900] [--poke 65=12] [--out chain.txt] [--every k] [--join f,L]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
TAIL = opt('--tail', ''); T1 = opt('--t1', 26900); POKES = opt('--poke', '65=12'); OUT = opt('--out', ''); EV = opt('--every', 10)
JOIN = opt('--join', ''); XMAX = opt('--xmax', 420)
ours = [row(l.strip()) for l in open(a[0]) if l.strip() and not l.startswith('#')]
fc = core(tas_mst(26607))
for p in [q for q in POKES.split(',') if q]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
fc.save('b'); fc._ka_slot = 'b'
KEYS = (0x86, 0x85, 0x8A, 0x84, 0x8C, 0x51, 0x52)  # vy is stale on the ground
def key_m(m): return tuple(m[k] for k in KEYS)
FN = {0x86: 'x86', 0x85: 'xsub', 0x8A: 'y8a', 0x89: 'vy', 0x87: 'vy_sub', 0x84: 'rf84', 0x8C: 'coll', 0x51: 'scr_lo', 0x52: 'scr_hi'}
if JOIN:
    fj, L = map(int, JOIN.split(','))
else:
    ext = ours + [('Left',)] * 60
    st = fc.run_batch('b', [ext], record='all')[0].states
    tk = {}
    for f in range(26610, 27000): tk.setdefault(key_m(TM(f)), f)
    fj = None
    for i, s in enumerate(st):
        f = 26608 + i
        if i < len(ours) - 1 or RXY(s)[0] > XMAX: continue
        k = tuple(s[FN[q]] for q in KEYS)
        if k in tk:
            fj, L = f, f - tk[k]; break
    print('join', fj, 'lag', L, 'TAS frame', fj - L if fj else None)
    if fj is None: sys.exit()
rows = (ours + [('Left',)] * 60)[:fj - 26608 + 1]
hist = [T(f) for f in range(26458, 26608)]
hist = [tuple(sorted(set(r) - ({'Left'} if {'Left','Right'} <= set(r) else set()) - ({'Up','Down'} if {'Up','Down'} <= set(r) else set()))) for r in hist]
en = A.Enforcer(hist + rows)
def want(f):
    w = set(T(f))
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    return tuple(sorted(w))
for f in range(fj - L + 1, T1 + 1): rows.append(tuple(sorted(en.emit(want(f)))))
if TAIL: rows += [row(l.strip()) for l in open(TAIL) if l.strip() and not l.startswith('#')]
print('legal:', legal_ok(rows, hist) or 'ok', 'rows', len(rows), 'last frame', 26607 + len(rows))
st = fc.run_batch('b', [rows + [()] * 30], record='all')[0].states
prev = None; firstdiv = None
for i, s in enumerate(st):
    f = 26608 + i; X, y = RXY(s)
    tf_ = f - L; ev = []
    if f > fj and tf_ <= 27012:
        tX, ty = tas_xy(tf_)
        if (X, y) != (tX, ty) and firstdiv is None: firstdiv = f; ev.append(f'DIVERGE from TAS {tf_} ({tX},{ty})')
    if prev:
        for k in ('hp65', 'np64', 'item', 'room6e'):
            if s[k] != prev[k]: ev.append(f'{k} {prev[k]}->{s[k]}')
    if ev or (EV and i % EV == 0):
        print(f, P(rows[i]) if i < len(rows) else '(pad)', f'X {X} y {y} hp {s["hp65"]} np {s["np64"]} rm {s["room6e"]} TASeq {tf_}', ' '.join(ev))
    prev = s
if OUT:
    with open(OUT, 'w') as fo:
        fo.write(f'# l53a room 27 chain: ours to {fj}, TAS rows {fj-L+1}..{T1} at lag {L}, tail {TAIL}\n')
        for r in rows: fo.write(P(r) + '\n')
fc.close()
