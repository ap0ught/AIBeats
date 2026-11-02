import sys
sys.path.insert(0, 'work/a56r2'); sys.path.insert(0, 'ng/stages')
import jplan as J, a56_common as C
from ng.inputs import read_inputs
e = C.open_emu("a56r2_probe.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    e.set_fields(dict(e.fields, pod_id=0x406, pod_hp=0x496))
    s0 = e.load('tmp/a56r2_64b_control')
    hist = list(read_inputs('logs/a56_6-4a_b11.inputs.txt'))[-1700:] + [()] * 151
    en = C.Enforcer(hist)
    # best depth-0 candidate: find by brute force over the same set, print the best one's rows
    root = J.Node(); root.sid = e.msave(); root.en = en; root.thp = 16
    cfg = J.CFGS['jaquio']
    res = []
    for pd in ['Right', 'Left', None]:
        for w in ([0, 4, 10, 18, 28] if pd else [8, 20]):
            for d in ['Right', None, 'RN', 'Left']:
                r = J.play_step(e, cfg, root, J.step_rows(pd, w, d, 2, 70), w)
                if r: res.append((r[1]['frame'], r[1]['x'], r[1]['y'], r[1]['anim'], pd, w, d))
    for x in sorted(res, key=lambda t: abs(t[1] - 110) + t[0] * 0.3)[:6]: print(x)
    b = sorted(res, key=lambda t: abs(t[1] - 110) + t[0] * 0.3)[0]
    rows = J.play_step(e, cfg, root, J.step_rows(b[4], b[5], b[6], 2, 70), b[5])[0]
    e.mload(root.sid); e.trace(True); e.run(rows + [()] * 3 + [('A',)] * 2 + [()] * 50)
    for s in e.last_trace[len(rows) - 3:]: print(s['frame'], s['x'], s['y'], s['anim'], s['pad'], s['vy'])
    e.screenshot('tmp/a56r2_jaq_plate')
finally:
    e.close()
