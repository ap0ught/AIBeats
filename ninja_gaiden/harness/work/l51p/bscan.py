"""$BF scan on a TAS section: Mesen TAS state S (after row S) with $BF poked to our value (c + S - 22125), legalized TAS rows
S+1..E (+ overrides 'f=ROW,f1-f2=ROW'), compare Ryu (X, y, hp) with the TAS per frame.
python work/l51p/bscan.py S E "<overrides>" c1 c2 ... | all | step:N"""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
S, E = int(sys.argv[1]), int(sys.argv[2]); ovs = sys.argv[3]; a = sys.argv[4:]
if a == ['all']: vals = list(range(256))
elif a and a[0].startswith('step:'): vals = list(range(0, 256, int(a[0][5:])))
else: vals = [int(v) for v in a]
ov = {}
for it in ovs.split(',') if ovs else []:
    k, v = it.split('='); k1, k2 = (k.split('-') + [k])[:2]
    for f in range(int(k1), int(k2) + 1): ov[f] = row(v)
want = []
for f in range(S + 1, E + 1):
    w = set(T(f))
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if f in ov: w = set(ov[f])
    want.append(tuple(sorted(w)))
hist = [T(f) for f in range(S - 100, S + 1)]
hist = [tuple(sorted(set(r) - ({'Left'} if 'Right' in r and 'Left' in r else set()))) for r in hist]
en = A.Enforcer(hist); rows = [tuple(sorted(en.emit(w))) for w in want]
print('legal:', legal_ok(rows, hist) or 'ok', '| changed by enforcer:', [(S + 1 + i, P(want[i]), P(rows[i])) for i in range(len(rows)) if tuple(sorted(want[i])) != rows[i]][:12], flush=True)
fc = core(tas_mst(S)); fc.save('b'); fc._ka_slot = 'b'
TXY = {f: tas_xy(f) + (TM(f)[0x65],) for f in range(S + 1, E + 1)}
for c in vals:
    fc.load('b'); fc.poke(0xBF, (c + S - 22125) % 256)
    _, recs, _ = fc.step(rows, record='all')
    first = None; hits = []; hp = TM(S)[0x65]
    for i, r in enumerate(recs):
        f = S + 1 + i; X, y = RXY(r)
        if r['hp65'] != hp: hits.append(f'{f}:{X},{y},{hp}->{r["hp65"]}'); hp = r['hp65']
        if first is None and (X, y, r['hp65']) != TXY[f]: first = (f, (X, y, r['hp65']), TXY[f])
    X, y = RXY(recs[-1])
    print(f'c {c:3d} first diff {first} | end {E} X {X} y {y} hp {recs[-1]["hp65"]} (TAS {TXY[E]}) | hits {hits}', flush=True)
fc.close()
