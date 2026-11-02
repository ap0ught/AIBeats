"""Trace stage rows from the base state: python work/l43/tr.py <stage rows> [from_frame] [to_frame] [step] [e]
Prints frame, row, room, X, y, hp, np, item, TAS X/y at the lag, enemies (with 'e'). Also saves the end state
with --save <name> (Mesen states/mesen/<name>.mst)."""
import sys
sys.path.insert(0, 'work/l43')
from lib import *
a = sys.argv[1:]
save = None
if '--save' in a:
    i = a.index('--save'); save = a[i + 1]; del a[i:i + 2]
rows = rows_file(a[0])
f1 = int(a[1]) if len(a) > 1 else CTL; f2 = int(a[2]) if len(a) > 2 else CTL + len(rows) - 1
st = int(a[3]) if len(a) > 3 else 1; E = len(a) > 4
print('legal:', legal_ok(rows, hist_chain()) or 'PASS', 'rows', len(rows), 'end frame', CTL + len(rows) - 1)
fc = core()
_, recs, _ = fc.step(rows, record='all')
for i, s in enumerate(recs):
    f = CTL + i
    if f < f1 or f > f2 or ((f - f1) % st and i != len(recs) - 1): continue
    t = f - LAG
    line = f"{f} {P(rows[i]):12s} rm{s['room']} X{C.abs_x(s)} y{s['y']} hp{s['hp']} np{s['ninpo']} it{s['item']} inv{s['inv']} | TAS rm{TRM.get(t)} X{TX.get(t)} y{TY.get(t)}"
    if E: line += ' | ' + ' '.join(f's{j}t{tt}@{x},{y}' for j, tt, x, y in enemies_s(s))
    print(line)
s = recs[-1]
print('END', CTL + len(rows) - 1, 'rm', s['room'], 'X', C.abs_x(s), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'item', s['item'], 'BF', s['bf'], 'e5c', s['e5c'])
if save:
    fc.save('z'); fc.save_file('z', f'states/mesen/{save}.mst', frame=CTL + len(rows) - 1); print('saved', save)
fc.close()
