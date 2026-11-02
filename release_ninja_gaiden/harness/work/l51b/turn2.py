"""w1 with the air turn moved to f (Left x2): build rows to 23,589, then TAS rows lag 509 to 23,130 eq; trace bird + hits.
python work/l51b/turn2.py f [save]"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
f = int(sys.argv[1]); SAVE = len(sys.argv) > 2
W = [set(r) for r in C.rows_of('work/l51a/w1_23589.txt')]
hist = [tuple(sorted(r)) for r in C.rows_of('logs/l44p_r1920_c2_poweron.inputs.txt')]
W[23298 - 22629] = {'Right'}; W[23299 - 22629] = {'Right'}
W[f - 22629] = {'Left'}; W[f + 1 - 22629] = {'Left'}
rows = enforce(W, hist); assert not legal_ok(rows, hist)
C.write_inputs(f'work/l51b/w1t{f}_23589.txt', rows, f'w1 rows with the air turn Left x2 on {f}-{f+1} (was 23,298-99)')
fc = core('states/mesen/lock_51_pre.mst')
_, recs, _ = fc.step(rows, record='all')
fc.save('w'); 
if SAVE:
    fc.save_file('w', f'states/mesen/l51b_w1t{f}_23589.mst', frame=23589)
    C.write_inputs(f'work/l51b/h_w1t{f}_23589.inputs.txt', hist + rows, 'power-on rows to 23,589')
    # also 23,559 state
    fc2 = core('states/mesen/lock_51_pre.mst'); fc2.step(rows[:23559 - 22628], record='last'); fc2.save('x')
    fc2.save_file('x', f'states/mesen/l51b_w1t{f}_23559.mst', frame=23559)
    C.write_inputs(f'work/l51b/h_w1t{f}_23559.inputs.txt', hist + rows[:23559 - 22628], 'power-on rows to 23,559'); fc2.close()
t = enforce(tasleg(23081, 23140), hist + rows)
_, r2, _ = fc.step(t, record='all')
allr = recs + r2
hp = 15
for i, r in enumerate(allr):
    g = 22629 + i
    if g < 23540: continue
    X, y = RXY(r); scr = X - r['x86']
    if (g % 3 == 0) or r['hp65'] != hp:
        print(g, g - 509, (X, y), 'hp', r['hp65'], ' '.join(f's{j}t{r[f"t{j}"]}({scr + r[f"ex{j}"]},{r[f"ey{j}"]})' for j in range(8) if r['eact'] >> j & 1))
    hp = r['hp65']
    if g > 23650: break
fc.close()
