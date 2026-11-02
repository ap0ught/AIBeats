import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/room46_6-4b'); f = s.frame
        e.run(R[f:38132]); sid = e.msave()
        def test(name, rows):
            e.mload(sid)
            tr = C.play_trace(e, rows)
            hits = [t['frame'] for a, t in zip([None] + tr, tr) if a is not None and t['boss_real'] != a['boss_real']]
            print(f'{name:10s} real {tr[-1]["boss_real"]:2d} hp {tr[-1]["hp"]} hits {hits}')
            print('     ', [(t['frame'], C.abs_x(t), t['y']) for t in tr[::4]][:16])
        for per in (5, 6):
            for d in ((), ('Left',), ('Down',)):
                rows = []
                for i in range(80):
                    r = list(d)
                    if i % per in (0, 1): r += ['B']
                    rows.append(tuple(r))
                test(f'p{per} {"+".join(d)}', C.legalize(rows))
    finally:
        e.close()
