import sys
sys.path.insert(0, 'work/l33')
from lib import *
tag = sys.argv[1]
FLD2 = dict(FLD); FLD2['bpose'] = 0x43F; FLD2['bhp'] = 0x497
for j in range(3): FLD2[f'fx{j}'] = 0x4BB + j; FLD2[f'fy{j}'] = 0x4BE + j
fc = core(tag, FLD2)
rows = [('Left',)] * 3 + [()] * 200
_, recs, _ = fc.step(rows, record='all'); fc.close()
for i, s in enumerate(recs):
    if i % 2 == 0: print(i + 1, 'boss', s['bx'] if 'bx' in s else '', s[f't7'], 'x', s.get('bx'), 'pose', s['bpose'], 'ryu', s['x'], s['y'], 'hp', s['hp'], 'e', hex(s['eact']), [s[f't{k}'] for k in range(8)], 'bf', s['bf'])
