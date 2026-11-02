import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load(sys.argv[1]); f = s.frame
        a, b = int(sys.argv[2]), int(sys.argv[3])
        e.run(R[f:a])
        for fr in range(a, b):
            e.step(R[fr], 1)
            if fr % 3: continue
            m = e.ram(0x400, 0xA0)
            st = e.state()
            ids = list(m[0:8]); xs = list(m[0x60:0x68]); ys = list(m[0x80:0x88]); hp = list(m[0x90:0x98])
            print(fr + 1, 'ryu', st['x'], st['y'], 'ids', ids, 'x', xs, 'y', ys, 'hp', hp)
    finally:
        e.close()
