"""NesHawk: trace the 3-1 start power-on file and save states/lock_31_ctl at its end (3-1 control 9,993)."""
import csv, sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'tools')
from ng.emulator import BizHawk, LOGS_DIR
from ng.inputs import read_inputs
from ng.mode import TICKS
src, tag, st = sys.argv[1], sys.argv[2], sys.argv[3]
rows = read_inputs(src)
e = BizHawk(log_name='l31alt_mkbase.log')
try:
    e.reset(); e.tick(TICKS); e.trace(True)
    out = []
    for i in range(0, len(rows), 1000):
        e.run(rows[i:i + 1000]); out.extend(e.last_trace)
    s = e.state(); print('end', {k: s.get(k) for k in ('frame', 'stage', 'gm', 'x', 'y', 'hp', 'ninpo', 'item', 'rng')}, flush=True)
    e.save(st)
finally:
    e.close()
p = LOGS_DIR / f'{tag}.trace.csv'
with open(p, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); keys = list(out[0].keys()); w.writerow(['row', 'input'] + keys)
    for i, (r, s) in enumerate(zip(rows, out)): w.writerow([i + 1, '+'.join(r)] + [s.get(k, 0) for k in keys])
print('wrote', p, len(out))
