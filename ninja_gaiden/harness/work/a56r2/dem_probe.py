import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
def slots(e):
    r = e.ram(0x400, 0xA0)
    return [(s, r[s], r[0x60+s], r[0x80+s], r[0x90+s]) for s in range(8) if r[s]]
if __name__ == "__main__":
    e = C.open_emu("a56r2_probe.log")
    try:
        e.load('ref4751/room47_6-5'); s = e.run([()] * 151); e.save('tmp/a56r2_65_control')
        print('control', s['frame'], s['x'], s['y'], s['rng'], s['timer'], s['subtimer'])
        for i in range(0, 260):
            s = e.run([()])
            if i % 10 == 0: print(s['frame'], s['x'], s['y'], s['boss_real'], slots(e))
    finally:
        e.close()
