"""NesHawk run of stage rows (row i -> frame 14,866 + i; file = rows after the control frame).
python work/l41/nh.py <rows> <out.bin> [--from <state name> (default lock_41q_ctlR)] [--save f:name,..] [--to f]
dump = 4-byte f0 + 2048 B per frame (as work/l41p/rundump.py)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
sys.path.insert(0, 'work/l41'); from lib import F0
from ng.mode import TICKS
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return v
    return d
st_name = opt('--from', 'lock_41q_ctlR'); saves = opt('--save', ''); to = opt('--to', None)
rf, out = a[0], a[1]
rows = C.rows_of(rf)
sv = {}
for q in saves.split(','):
    if q: f, n = q.split(':'); sv[int(f)] = n
e = C.open_emu('l41_nh.log')
rams = []
try:
    e.tick(TICKS)
    st = e.load(st_name); f0 = st['frame']
    end = F0 + len(rows) if to is None else int(to)
    cur = f0
    pts = sorted(k for k in sv if f0 < k <= end) + [end]
    for p in pts:
        _, rr = e.run_ram(rows[cur - F0:p - F0]); rams += rr; cur = p
        if p in sv: e.save(sv[p]); print('saved', sv[p], 'at', p)
finally:
    e.close()
with open(out, 'wb') as f:
    f.write(f0.to_bytes(4, 'little'))
    for m in rams: f.write(m)
print('f0', f0, 'frames', len(rams))
