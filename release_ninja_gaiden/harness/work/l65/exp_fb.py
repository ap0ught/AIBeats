import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
tas = rows_of('work/l63p/tas65_fight.txt')
fc = core65()
for v in [243, 0, 150]:
    for tail in [[('Left',)] * 60 + [()] * 140, [()] * 200]:
        rows = tas[:121] + tail
        fc.load('c0'); fc.poke(0xBF, v); fc.save('x')
        st = fc.run_batch('x', [rows], record='all')[0].states
        out = []
        for i in range(121, len(st), 8):
            s = st[i]
            out.append((i + 1, s['x86'], s['hp65'], [(j, s[f'ex{j}'], s[f'ey{j}']) for j in range(8) if s[f't{j}'] == 41]))
        print('bf', v, 'tail', 'L' if tail[0] else '-', out[:14], flush=True)
fc.close()
