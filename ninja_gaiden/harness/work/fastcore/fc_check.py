"""fastcore self-check: boot + STEP and RUN vs the NesHawk TAS trace (pads = NesHawk's effective pad bytes)."""
import sys, time
sys.path.insert(0, '.')
from ng.fastcore import FastCore, neshawk_pads
import csv
tr = {}
with open('logs/tas4751.trace.csv') as f:
    for r in csv.DictReader(f):
        tr[int(r['row'])] = r
pads = neshawk_pads('logs/tas4751.trace.csv', 39084)
names = ['x', 'y', 'stage', 'room', 'hp', 'timer', 'rng', 'pad', 'padnew', 'bosshp', 'scroll', 'xsub', 'gm', 'cs', 'lagged']
def cmp(recs, f0):
    bad = []
    for i, r in enumerate(recs):
        t = tr[f0 + i]
        d = [k for k in names if int(t[k]) != r[k]]
        if d: bad.append((f0 + i, d))
    return bad
with FastCore(boot_rows=pads[:174]) as fc:
    fc.save('c174')
    n, recs, st = fc.step(pads[174:5174], record='all')
    print('step 175..5174', n, st, 'frame now', fc.frame, 'diffs', len(cmp(recs, 175)), cmp(recs, 175)[:3])
    fc.save('c5174')
    # batch: 3 candidates from 5174: the TAS rows, the same again, and a variant
    c = pads[5174:5674]
    res = fc.run_batch('c5174', [c, c, bytes([0x01]) * 500], record='all', record_ram=True)
    print('batch statuses', [(r.rows_played, r.status) for r in res], 'cand0 diffs', len(cmp(res[0].states, 5175)),
          'cand0==cand1', res[0].states == res[1].states and res[0].ram == res[1].ram, 'variant diffs', len(cmp(res[2].states, 5175)))
    # stop condition: room change
    res = fc.run_batch('c174', [pads[174:3000]], record='last', stops=[(0x6E, 'changed', 0)], start_frame=174)
    r = res[0]
    print('stop on room change: played', r.rows_played, 'status', r.status, 'frame', r.states[-1]['frame'], 'room', r.states[-1].room,
          'trace room at that frame', tr[174 + r.rows_played]['room'], 'prev', tr[174 + r.rows_played - 1]['room'])
