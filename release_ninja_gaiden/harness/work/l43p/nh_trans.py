"""NesHawk: 4-3 -> 4-4 transition rules on the TAS path. TAS rows from ref4751/10_4-3_control to row 21,073 (trigger
21,074 = first $5C 2->0 at X 748 y 208), then variants of Start / pre-control Left; report load frame ($6D 10->11),
first frame Ryu's x moves (Left held), x on the 4-4 control frame."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
def T(f): return tuple(TR[f - 1])
e = C.open_emu('l43p_nhtrans.log')
def run(rows, f0):
    _, rams = e.run_ram(rows)
    load = ctl = None; xs = []
    x0 = None
    for i, m in enumerate(rams):
        f = f0 + 1 + i
        if load is None and m[0x6D] == 11: load = f
        if load and m[0x6D] == 11:
            xs.append((f, m[0x86], m[0x8A]))
    return load, xs, rams
try:
    e.tick(TICKS)
    st = e.load('ref4751/10_4-3_control'); f0 = st['frame']; print('state', f0, flush=True)
    _, rams = e.run_ram([T(f) for f in range(f0 + 1, 21074)])
    m = rams[-1]; print('after 21073: X', m[0x52]*256 + m[0x51] + m[0x86], 'y', m[0x8A], '5C', m[0x5C], 'st', m[0x6D], flush=True)
    base = e.msave()
    N = 21360 - 21073
    def variant(tag, rows):
        e.mload(base)
        load, xs, rams = run(rows, 21073)
        # trigger
        trig = next((21074 + i for i, mm in enumerate(rams) if mm[0x5C] == 0), None)
        mv = next(((f, x, y) for (f, x, y), (f2, x2, y2) in zip(xs, xs[1:]) if x2 != x), None)
        x_at = {f: (x, y) for f, x, y in xs}
        print(f'{tag:28s} trigger {trig} load {load} first x change after load {mv} x@21353 {x_at.get(21353)} x@21354 {x_at.get(21354)} x@21355 {x_at.get(21355)}', flush=True)
    blank = [()] * N
    def leftfrom(k, rows=None):
        r = list(rows or blank)
        for f in range(k, 21361): r[f - 21074] = tuple(sorted(set(r[f - 21074]) | {'Left'}))
        return r
    def start_at(k, rows=None):
        r = list(rows or blank); r[k - 21074] = ('Start',); r[k - 21073] = ('Start',); return r
    variant('TAS rows', [T(f) for f in range(21074, 21361)])
    variant('Left from 21354', leftfrom(21354))
    variant('Left from 21353', leftfrom(21353))
    variant('Left from 21352', leftfrom(21352))
    variant('Left from 21340', leftfrom(21340))
    variant('Left from 21300', leftfrom(21300))
    variant('Left from 21210', leftfrom(21210))
    for k in (21075, 21090, 21120, 21150, 21190, 21203, 21206, 21215, 21230, 21260, 21300, 21340):
        variant(f'Start {k}-{k+1}, Left 21354', leftfrom(21354, start_at(k)))
finally:
    e.close()
