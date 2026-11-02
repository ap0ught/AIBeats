"""When does the heart come down if the pod dies later? TAS rows with w extra blank rows at the start (pod dies at +108+w)."""
import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
FLD['pst6'] = 0x42E
tas = rows_of('work/l63p/tas65_fight.txt')
fc = core65()
for w in [0, 5, 10, 11, 12, 13, 15, 20, 40, 60, 75, 76]:
    for v in [243, 37, 0, 150]:
        rows = [()] * w + tas[:115] + [()] * 300
        fc.load('c0'); fc.poke(0xBF, v); fc.save('x')
        st = fc.run_batch('x', [rows], record='all')[0].states
        pk = next((i + 1 for i, s in enumerate(st) if s['t6'] == 38 and s['pst6'] == 60), None)
        fr = [i + 1 for i in range(1, len(st)) if st[i]['t6'] == 41 and (st[i-1]['t6'] != 41 or st[i]['ey6'] < st[i-1]['ey6'] - 20)]
        hd = next((i + 1 for i, s in enumerate(st) if s['ey7'] == 168), None)
        spawns = [i + 1 for i in range(1, len(st)) for j in range(8) if st[i][f't{j}'] == 41 and st[i - 1][f't{j}'] != 41]
        print('w', w, 'bf', v, 'pod dead row', pk, 'heart down row', hd, 'type-41 spawns', spawns[:6], 'hp', st[-1]['hp65'], flush=True)
fc.close()
