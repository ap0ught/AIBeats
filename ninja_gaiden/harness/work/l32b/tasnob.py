import sys
sys.path.insert(0, 'work/l32b'); sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
import xp, a56_common as A
from ng.solve import common as C
TR = A.tas_rows()
k0 = int(sys.argv[1]); k1 = int(sys.argv[2]); ev = int(sys.argv[3]) if len(sys.argv) > 3 else 2
rows = [tuple(x for x in r if x != 'B') for r in TR[k0:k1]]
st = xp.run(f'states/mesen/l32b_tas{k0}.mst', rows)
for i, s in enumerate(st):
    if i % ev: continue
    scr = C.abs_x(s) - s['x']
    en = ' '.join(f"{j}:t{s[f't{j}']}s{s[f's{j}']}@{scr + s[f'x{j}']},{s[f'y{j}']}" for j in range(8) if s['eb'] >> j & 1)
    print(k0 + i + 1, '+'.join(rows[i]) or '-', 'X', C.abs_x(s), 'y', s['y'], 'an', s['anim'], 'fl', hex(s['rflags']), 'inv', s['inv'], 'hp', s['hp'], en)
