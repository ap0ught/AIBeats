import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/12_5-1_control'); f = s.frame
        e.run(R[f:22368]); sid = e.msave()
        for wait in range(0, 12, 2):
            for d in ('Right',):
                e.mload(sid)
                rows = [('Right',)] * wait + [('Right', 'A'), ('Right', 'A')] + [('Right',)] * 40
                tr = C.play_trace(e, rows)
                path = [(t['frame'], C.abs_x(t), t['y'], t['hp']) for t in tr[::4]]
                print(wait, path[:14])
    finally:
        e.close()
