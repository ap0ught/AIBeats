import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/12_5-1_control'); f = s.frame
        e.run(R[f:22373]); sid = e.msave()
        print(e.state())
        for pre in ([], [('Left',)]*2, [()]*2, [('Right',)]*2):
            for jl in (2, 10, 20):
                e.mload(sid)
                rows = pre + [('Right', 'A')]*jl + [('Right',)] * (40-jl)
                tr = C.play_trace(e, rows)
                path = [(C.abs_x(t), t['y'], t['hp']) for t in tr[::3]]
                print(len(pre), pre[:1], jl, path[:15])
    finally:
        e.close()
