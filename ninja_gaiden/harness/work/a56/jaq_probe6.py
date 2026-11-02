import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/room46_6-4b'); f = s.frame
        for start in (38131, 38132):
            e.load('ref4751/room46_6-4b'); e.run(R[f:start])
            for d in ((), ('Left',), ('Right',)):
                sid = e.msave()
                cyc = [('Down',) + d, ('Down', 'B') + d, ('B',) + d, d, d]
                rows = (cyc * 12)[:60]
                print('legal' if __import__('check_inputs').check(rows)['pass'] else 'ILLEGAL', end=' ')
                tr = C.play_trace(e, rows)
                hits = [t['frame'] for a, t in zip([None] + tr, tr) if a is not None and t['boss_real'] != a['boss_real']]
                print(start, d, 'real', tr[-1]['boss_real'], 'hp', tr[-1]['hp'], 'hits', hits, [(C.abs_x(t), t['y']) for t in tr[::6]])
                e.mload(sid)
    finally:
        e.close()
