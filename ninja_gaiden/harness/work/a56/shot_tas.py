import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    st, frames = sys.argv[1], [int(x) for x in sys.argv[2].split(',')]
    R = C.tas_rows()
    e = C.open_emu("a56_shot.log")
    try:

        s = e.load(st); f = s.frame
        for fr in frames:
            e.run(R[f:fr]); f = fr
            e.screenshot(f"a56/tas_{fr}")
            print(fr, e.state())
    finally:
        e.close()
