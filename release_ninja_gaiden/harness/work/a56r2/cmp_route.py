"""Compare time-to-reach abs x (per room) for the TAS, the record (video trace) and our legal solutions.
    python work/a56r2/cmp_route.py <stage idx> <record json> [our .ref.json ...] [--step 64]"""
import json, sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
a = sys.argv[1:]
stage = int(a[0]); rec = json.load(open(a[1]))
ours = a[2:]
ts = C.tas_stage(stage); T = C.tas_trace()
ctl = ts['control']; end = C.tas_stage(stage + 1)['load'] if stage < 21 else 39084
def firsts(seq):  # seq of (t, room, absx, y) -> {(room, bucket): t} first reach of a bucket (monotone max x per room)
    out = {}; 
    for t, room, ax, y in seq:
        b = ax // 64
        out.setdefault((room, b), t)
    return out
tasq = [(k - ctl, T[k]['room'], C.abs_x(T[k]), T[k]['y']) for k in range(ctl, end)]
room0 = T[ctl]['room']
recq = [(r['t'], room0 + r['room'], r['scroll'] + r['sx'] - 2, r['sy'] + 9) for r in rec['rows'] if r['sx'] is not None and r['t'] >= 0 and r['n'] >= 12]
# per-room calibration: the record's first point in a room = the TAS's first point in that room (same spawn)
tfirst = {}
tent = {}
for t, room, ax, y in tasq: tent.setdefault(room, t)
for t, room, ax, y in tasq:
    if t >= tent[room] + 40: tfirst.setdefault(room, ax)
rent = {}
for t, room, ax, y in recq: rent.setdefault(room, t)
rfirst = {}
for t, room, ax, y in recq:
    if t >= rent[room] + 17: rfirst.setdefault(room, ax)
r0 = next(q for q in recq if q[1] == room0)
tfirst[room0] = C.abs_x(T[ctl + int(r0[0])]); rfirst[room0] = r0[2]
recq = [(t, room, ax + tfirst.get(room, rfirst[room]) - rfirst[room], y) for t, room, ax, y in recq]
qs = {'TAS': firsts(tasq), 'REC': firsts(recq)}
for o in ours:
    rj = json.load(open(o)); tr = rj['trace']; f0 = rj['start']['frame']
    seq = [(int(k) - f0, v['room'], C.abs_x(v), v['y']) for k, v in sorted(tr.items(), key=lambda kv: int(kv[0])) if v['stage'] == stage]
    qs[o.split('/')[-1][:18]] = firsts(seq)
keys = sorted(set(qs['TAS']) | set(qs['REC']))
print('room bucket(x/64)', *qs.keys(), sep='\t')
for k in keys:
    print(k, *[qs[n].get(k, '') for n in qs], sep='\t')
print('TAS end (next load - control)', end - ctl)
