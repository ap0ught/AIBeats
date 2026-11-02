import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); T = C.tas_trace(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/room46_6-4b'); f = s.frame
        e.run(R[f:38131]); sid = e.msave()
        def test(name, rows):
            e.mload(sid)
            tr = C.play_trace(e, rows)
            hits = [(t['frame'], t['bosshp']) for a, t in zip([None] + tr, tr) if a is not None and t['bosshp'] != a['bosshp']]
            print(name, 'bosshp', tr[-1]['bosshp'], 'hp', tr[-1]['hp'], 'hits', hits[:20], 'pos', C.abs_x(tr[-1]), tr[-1]['y'])
        test('TAS', R[38131:38190])
        for per in (2, 3, 4, 5, 6):
            for d in ((), ('Down',)):
                rows = []
                for i in range(60):
                    r = list(d)
                    if i % per in (0,) : r.append('B')
                    if per >= 4 and i % per == 1: r.append('B')
                    rows.append(tuple(r))
                test(f'per{per}{"D" if d else ""}', rows)
    finally:
        e.close()
