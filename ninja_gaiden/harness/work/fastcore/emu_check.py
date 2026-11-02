import sys, csv; sys.path.insert(0, '.')
from ng.fastcore import MesenEmu
from ng.inputs import read_inputs
rows = read_inputs('logs/a12r3_to22.inputs.txt')
tr = {int(r['row']): r for r in csv.DictReader(open('logs/fc_to22.trace.csv'))}
with MesenEmu(boot_rows=rows[:174]) as e:
    s = e.state(); print('start frame', s.frame)
    sid = e.msave()
    e.trace(True)
    s = e.run(rows[174:400]); print('frame', s.frame, 'x', s.x, 'trace x', tr[400]['x'], 'gm', s.gm, 'len trace', len(e.last_trace))
    bad = [t.frame for t in e.last_trace if any(int(tr[t.frame][k]) != t[k] for k in ('x', 'y', 'rng', 'gm', 'lagged', 'scroll'))]
    print('trace mismatches', bad[:5])
    e.mload(sid); s = e.state(); print('after mload frame', s.frame, 'inputs', len(e.inputs))
    s = e.step('Right', 10); print('step frame', s.frame)
    p = e.save('fc_test_400'); print('saved', p)
    e.mload(sid); s = e.run(rows[174:400]); print('rerun frame', s.frame, 'x', s.x)
    s = e.load('fc_test_400'); print('loaded file frame', s.frame, 'x', s.x)
