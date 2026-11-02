import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    st, rowsf, name = sys.argv[1], sys.argv[2], sys.argv[3]
    back = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else [0]
    rows = C.read_inputs(rowsf)
    e = C.open_emu("a56_shot.log")
    try:
        e.load(st)
        n = len(rows)
        done = 0
        for b in sorted(back, reverse=True):
            e.run(rows[done:n - b]); done = n - b
            s = e.state(); e.screenshot(f"a56/{name}_{b}")
            print(b, s['frame'], C.abs_x(s), s['y'], s['hp'], s['room'])
    finally:
        e.close()
