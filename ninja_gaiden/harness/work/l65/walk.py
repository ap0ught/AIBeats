import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
FLD['pst6'] = 0x42E
P1 = rows_of('work/l65/podP1.txt')
fc = core65()
for v in [60, 0, 1, 2, 3]:
    for wt0 in [0, 20, 40]:
        rows = P1 + [()] * wt0 + [('Right',)] * 60 + [()] * 30
        fc.load('c0'); fc.poke(0xBF, v); fc.save('x')
        st = fc.run_batch('x', [rows], record='all')[0].states
        ev = []
        for i in range(124, len(st)):
            if st[i]['hp65'] < st[i-1]['hp65']:
                s = st[i]; ev.append((i + 1, s['x86'], s['y8a'], [(j, s[f't{j}'], s[f'ex{j}'], s[f'ey{j}']) for j in range(8) if s[f't{j}'] in (38, 41)]))
        print(v, wt0, 'X at end', st[-1]['x86'], 'hits', ev[:3], flush=True)
fc.close()
