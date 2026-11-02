"""Per-room 64-px column first-reach times: TAS vs record (t = NES frames after the stage's control).
    python work/a12r2/cmp.py <stage> <rec json> [our trace .json from a12r2 (list of [frame, room, X, y]) f0]"""
import sys
sys.path.insert(0, '.')
from ng import legal
st = int(sys.argv[1]); wp = legal.Waypoints(sys.argv[2], st)
T = wp.tas; c = wp.tas_c
tas = {}
for k in range(c, wp.tas_end):
    d = T.at(k); tas.setdefault((d['room'], legal._absx(d) // 64), k - c)
rec = wp.columns()
keys = sorted(set(tas) | set(rec), key=lambda q: (wp.rooms.index(q[0]) if q[0] in wp.rooms else 99, min(tas.get(q, 1e9), rec.get(q, 1e9))))
print('room col  TAS  REC  REC-TAS')
for q in keys:
    a, b = tas.get(q), rec.get(q)
    print(q[0], q[1], a if a is not None else '-', round(b) if b is not None else '-', round(b - a) if a is not None and b is not None else '')
print('TAS load - control', wp.tas_end - c, ' record last image t', wp.tend)
