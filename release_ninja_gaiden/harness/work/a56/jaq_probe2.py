import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/room46_6-4b'); f = s.frame
        e.run(R[f:38131]); sid = e.msave()
        def test(name, rows):
            e.mload(sid)
            tr = C.play_trace(e, rows)
            hits = [t['frame'] for a, t in zip([None] + tr, tr) if a is not None and t['bosshp'] != a['bosshp']]
            print(f'{name:14s} bosshp {tr[-1]["bosshp"]:2d} hp {tr[-1]["hp"]} hits {hits[:16]}', 'path', [(C.abs_x(t), t['y']) for t in tr[::6]][:10])
        for d in ((), ('Left',), ('Right',), ('Down',), ('Down', 'Left'), ('Down', 'Right')):
            for off in (0, 2):
                rows = [tuple(d) + (('B',) if (i - off) % 5 in (0, 1) and i >= off else ()) for i in range(60)]
                test(f'{"+".join(d) or "none"} o{off}', C.legalize(rows))
    finally:
        e.close()
