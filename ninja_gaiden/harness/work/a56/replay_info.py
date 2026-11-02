import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    st, rowsf = sys.argv[1], sys.argv[2]
    pre = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rows = C.read_inputs(rowsf)
    e = C.open_emu("a56_probe.log")
    try:
        e.load(st)
        if pre: e.run([()] * pre)
        out = []
        for r in rows:
            e.step(r, 1)
            s = e.state(); m = e.ram(0x470, 24)
            out.append((s['frame'], '+'.join(r), C.abs_x(s), s['y'], s['hp'], s['bosshp'], s['boss_real'], m[7], m[23], [m[i] for i in range(8)]))
        prev = None
        for o in out:
            if prev is None or o[6] != prev[6] or o[0] % 10 == 0:
                print(o)
            prev = o
    finally:
        e.close()
