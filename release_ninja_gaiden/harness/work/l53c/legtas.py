"""legalized TAS rows f1..f2 -> file, and check the positions vs the TAS. python work/l53c/legtas.py F0 f2 out"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
F0, f2, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
hist = legalize_tas(F0 - 150, F0)
rows = A.Enforcer(hist)
want = []
for f in range(F0 + 1, f2 + 1):
    w = set(T(f))
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    want.append(tuple(sorted(rows.emit(tuple(sorted(w))))))
print('legal:', legal_ok(want, hist) or 'ok')
fc = core_at(F0)
st = fc.run_batch(fc._ka_slot, [want], record='all')[0].states
d = [(F0 + 1 + i, RXY(s), tas_xy(F0 + 1 + i), s['hp65'], TM(F0 + 1 + i)[0x65]) for i, s in enumerate(st) if RXY(s) != tas_xy(F0 + 1 + i) or s['hp65'] != TM(F0+1+i)[0x65]]
print('diffs', len(d), d[:5])
open(out, 'w').write(f'# legalized TAS rows {F0+1}..{f2}\n' + '\n'.join(P(x) for x in want) + '\n')
fc.close()
