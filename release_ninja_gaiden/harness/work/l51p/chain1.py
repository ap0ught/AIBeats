"""Chain test: head start + legalized TAS rows at lag LAG (TAS row t -> our frame t+LAG) with Left x2 at TAS 22,793-94 and
A+Right one frame early at 23,279; reports hits, X at TAS checkpoints (+lag), from the TAS 22,124 state with $BF poke.
python work/l51p/chain1.py LAG END c1 c2 ..."""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
LAG = int(sys.argv[1]); END = int(sys.argv[2]); cs = [int(x) for x in sys.argv[3:]]
head = [tuple(sorted(r)) for r in C.rows_of('work/l51p/pre51_22490.txt')]
want = [set(r) for r in head]
for t in range(22490 - LAG + 1, END + 1):
    w = set(T(t))
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    if t in (22793, 22794): w = {'Left'}
    if t == 23279: w = {'A', 'Right'}
    if t == 23280: w = {'A', 'Right'}
    want.append(w)
en = A.Enforcer([()] * 60); rows = [tuple(sorted(en.emit(w))) for w in want]
print('legal', legal_ok(rows, [()] * 60) or 'ok', len(rows), flush=True)
fc = core(tas_mst(22124)); fc.save('b'); fc._ka_slot = 'b'
CK = [22600, 22800, 22957, 23080, 23100]
for c in cs:
    fc.load('b'); fc.poke(0xBF, (c - 1) % 256)
    _, recs, _ = fc.step(rows, record='all')
    hp = 16; hits = []; xs = []
    for i, r in enumerate(recs):
        f = 22125 + i; X, y = RXY(r)
        if r['hp65'] != hp: hits.append(f'{f}:{X},{y},{hp}->{r["hp65"]}'); hp = r['hp65']
        if f - LAG in CK: xs.append(f'{f - LAG}:{X},{y} (TAS {tas_xy(f - LAG)})')
    print(f'c {c}: hits {hits} | {xs}', flush=True)
fc.close()
