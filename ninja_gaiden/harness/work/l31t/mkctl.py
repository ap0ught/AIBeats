"""NesHawk: power-on file -> trace csv + state at its end. python work/l31t/mkctl.py <power-on file> <state name> <trace name>"""
import sys, csv
sys.path.insert(0, '.'); sys.path.insert(0, 'tools')
from ng.emulator import LOGS_DIR
from ng.inputs import read_inputs
import trace_run as T
from ng.emulator import BizHawk
from ng.mode import TICKS
rows = read_inputs(sys.argv[1]); name, tn = sys.argv[2], sys.argv[3]
e = BizHawk(log_name='l31t_mkctl.log')
try:
    e.reset(); e.tick(TICKS); e.trace(True)
    out = []
    for i in range(0, len(rows), 1000):
        e.run(rows[i:i+1000]); out.extend(e.last_trace)
    s = e.state(); e.save(name)
    print('end', {k: s.get(k) for k in ('frame', 'stage', 'room', 'x', 'y', 'hp', 'ninpo', 'item', 'rng')})
finally:
    e.close()
p = LOGS_DIR / f"{tn}.trace.csv"
with open(p, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); keys = list(out[0].keys()); w.writerow(['row', 'input'] + keys)
    for i, (r, s) in enumerate(zip(rows, out)):
        w.writerow([i + 1, '+'.join(r)] + [s.get(k, 0) for k in keys])
print('wrote', p, len(out))
