"""Legal chain a12r3_to22 (6,393 rows): NesHawk conflicts; Mesen clean-read replay vs NesHawk trace."""
import sys, csv
sys.path.insert(0, '.')
from ng.fastcore import FastCore
from ng.inputs import read_inputs, to_mask
rows = [to_mask(r) for r in read_inputs(sys.argv[1])]
tr = {}
with open(sys.argv[2]) as f:
    for r in csv.DictReader(f):
        tr[int(r['row'])] = r
conf = [k for k in sorted(tr) if tr[k]['lagged'] == '0' and int(tr[k]['pad']) != rows[k - 1]]
chg = sum(1 for k in range(2, len(rows) + 1) if rows[k - 1] != rows[k - 2])
print('rows', len(rows), 'input changes', chg, 'NesHawk conflict frames (pad != row)', len(conf), conf[:20])
names = ['x', 'y', 'stage', 'room', 'hp', 'timer', 'rng', 'pad', 'bosshp', 'scroll', 'xsub', 'gm', 'lagged']
for label, boot in (('clean rows', bytes(rows)), ('NesHawk pads', bytes(int(tr[k]['pad']) for k in range(1, len(rows) + 1)))):
    # replay via STEP from the checkpoint after row 174 (boot) to the end, record all
    with FastCore(boot_rows=boot[:174]) as fc:
        n, recs, st = fc.step(boot[174:], record='all')
    first = None
    for i, r in enumerate(recs):
        t = tr[175 + i]
        d = [k for k in names if int(t[k]) != r[k]]
        if d:
            first = (175 + i, d); break
    print(label, ': first difference', first)
