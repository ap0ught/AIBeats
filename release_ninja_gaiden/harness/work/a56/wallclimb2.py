import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
def cyc(k, first=('Left',), back='Right', nA=2):
    return [first + ('A',)] * nA + [(back,)] * (k - nA)
if __name__ == "__main__":
    start = int(sys.argv[1]); state = sys.argv[2]; n = 40
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load(state); f = s.frame
        e.run(R[f:start]); sid = e.msave()
        for name, p in [('L5', cyc(5)), ('L6', cyc(6)), ('L7', cyc(7)), ('L8', cyc(8)), ('n5', cyc(5, ())), ('n6', cyc(6, ())),
                        ('R5', cyc(5, ('Right',))), ('L5x', [('Left','A'),('Left','A'),('Right',),('Right',),('Right',),('Right',),('Right',),('Right',),('Right',),('Right',)])]:
            e.mload(sid)
            rows = C.legalize((p * 20)[:n])
            tr = C.play_trace(e, rows)
            print(f'{name:4s}', ' '.join(f'{C.abs_x(t)},{t["y"]}' for t in tr[::2][:20]))
    finally:
        e.close()
