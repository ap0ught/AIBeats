import sys
sys.path.insert(0, 'work/l33')
from lib import *
tag = sys.argv[1]; spec = sys.argv[2]; n = int(sys.argv[3])
FLD2 = dict(FLD)
for j in range(3): FLD2[f'fx{j}'] = 0x4BB + j; FLD2[f'fy{j}'] = 0x4BE + j
rows = []
for part in spec.split(','):
    w, k = part.split('*') if '*' in part else (part, '1')
    rows += [row(w)] * int(k)
rows += [()] * (n - len(rows))
lg = legal_after([], rows, hist(tag))
fc = core(tag, FLD2)
_, recs, _ = fc.step(lg, record='all'); fc.close()
for i, (w, s) in enumerate(zip(lg, recs)):
    print(i + 1, '+'.join(w) or '-', 'ryu', s['x'], s['y'], 'an', s['anim'], 'np', s['ninpo'], 'boss', s['bosshp'], s['bx'], s['by'], 'C8', s['thrown'], 'f', [(s[f'fx{j}'], s[f'fy{j}']) for j in range(3)], 'hp', s['hp'])
