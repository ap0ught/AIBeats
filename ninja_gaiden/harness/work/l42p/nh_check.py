"""NesHawk checks: (a) c3b + Right on the 4-2 control row 17,020 (x 64 -> 65.5); Right earlier does nothing;
(b) 4-2 -> 4-3: TAS rows to the trigger 18,680, Start on 18,681-82 or none; load frame and first Left move."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
S = C.rows_of('logs/l41_c3b.inputs.txt')
e = C.open_emu('l42p_nh.log')
try:
    e.tick(TICKS)
    for k in (0, 1, 5):
        st = e.load('lock_41q_pre'); f = st['frame']
        rows = list(S)
        for j in range(k): rows[-1 - j] = ('Right',)
        e.run(rows[:-1]); s0 = e.state(); e.run(rows[-1:]); s1 = e.state(); e.run([('Right',)]); s2 = e.state()
        print('Right on last', k, 'rows: frame', s1['frame'], 'x/xsub', s0['x'], s0['xsub'], '->', s1['x'], s1['xsub'], '->', s2['x'], s2['xsub'], 'BF', s1['rng'], 'stage', s1['stage'], flush=True)
    for sf in (None, 18681, 18700):
        st = e.load('ref4751/09_4-2_control'); f0 = st['frame']
        rows = list(TR[f0:18680])
        tail = []
        for f in range(18681, 18966):
            if sf and f in (sf, sf + 1): tail.append(('Start',))
            elif f >= 18900: tail.append(('Left',))
            else: tail.append(())
        e.run(rows)
        load = ctl = None; px = None
        for i, r in enumerate(tail):
            s = e.step(r) if hasattr(e, 'step') else None
            s = e.state()
            fr = 18681 + i
            if load is None and s['stage'] == 10: load = fr
            if fr > 18900 and ctl is None and px is not None and s['x'] != px: ctl = fr
            px = s['x']
        print('Start', sf, 'load', load, 'first Left move', ctl, flush=True)
finally:
    e.close()
