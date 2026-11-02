import sys, time
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    e = C.open_emu("a56r2_probe.log")
    try:
        e.load('tmp/a56r2_65_control')
        rows = [('Right',)] * 36 + [('Right', 'A'), ('Right', 'A')]
        cyc = [('Down', 'Right'), ('Down', 'B', 'Right'), ('B', 'Right'), ('Right',), ('Right',)]
        rows += (cyc * 20)
        t = time.time()
        for i, r in enumerate(rows):
            s = e.run([r])
            m = e.ram(0x80, 4); hp = e.ram(0x495, 3)
            print(s['frame'], r, s['x'], s['y'], s['vy'], m.hex(), list(hp), s['hp'])
        print('time', time.time() - t)
        e.load('tmp/a56r2_65_control'); t = time.time()
        for k in range(20): e.run(rows)
        print('20 x', len(rows), time.time() - t)
    finally:
        e.close()
