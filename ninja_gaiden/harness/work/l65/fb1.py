import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
P1 = rows_of('work/l65/podP1.txt')
rows = P1 + [()] * 110
fc = core65()
for v in list(range(0, 256, 1)):
    fc.load('c0'); fc.poke(0xBF, v); fc.save('x')
    st = fc.run_batch('x', [rows], record='all')[0].states
    def fbs(i):
        s = st[i - 1]; return [(s[f'ex{j}'], s[f'ey{j}']) for j in range(8) if s[f't{j}'] == 41]
    hd = next((i + 1 for i, s in enumerate(st) if s['ey7'] == 168), None)
    print(v, 'hd', hd, 'r130', fbs(130), 'r145', fbs(145), 'r160', fbs(160), 'r180', fbs(180), 'r200', fbs(200), flush=True)
fc.close()
