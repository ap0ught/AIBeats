import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows()
    e = C.open_emu("a56r2_probe.log")
    try:
        s = e.load('tmp/a56r2_65_control'); f = s['frame']
        prev = None
        for k in range(f, 39084):
            s = e.run([R[k]])
            hp = list(e.ram(0x490, 8)); ids = list(e.ram(0x400, 8)); xs = list(e.ram(0x460, 8)); ys = list(e.ram(0x480, 8))
            if hp != prev or k % 10 == 0:
                print(s['frame'], R[k], s['x'], s['y'], s['hp'], hp[5:], ids[5:], xs[5:], ys[5:])
            prev = hp
    finally:
        e.close()
