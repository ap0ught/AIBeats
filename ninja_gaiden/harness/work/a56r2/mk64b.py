import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
e = C.open_emu("a56r2_probe.log")
try:
    e.load('ref4751/room46_6-4b'); s = e.run([()] * 151); e.save('tmp/a56r2_64b_control')
    print(s['frame'], s['x'], s['y'], list(e.ram(0x400, 8)), list(e.ram(0x490, 8)), s['boss_real'])
    e.load('ref4751/19_6-4a_control'); s = e.state()
    print('6-4a', s['frame'], s['x'], s['y'], list(e.ram(0x400, 8)), list(e.ram(0x490, 8)), s['boss_real'], s['item'], s['ninpo'])
    for i in range(6):
        s = e.run([()] * 10); print(s['frame'], list(e.ram(0x400, 8)), list(e.ram(0x460, 8)), list(e.ram(0x480, 8)), list(e.ram(0x490, 8)))
finally:
    e.close()
