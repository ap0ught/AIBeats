"""NesHawk trace of a rows file from ref4751/09_4-2_control with $BF poked at control; compare with a Mesen trace.
python work/l42p/nhtrace.py <rows> <c> <mesen trace>"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
rows = C.rows_of(sys.argv[1]); c = int(sys.argv[2])
M = {int(l.split()[0]): l.split()[1:] for l in open(sys.argv[3])}
e = C.open_emu('l42p_nht.log')
try:
    e.tick(TICKS); e.load('ref4751/09_4-2_control'); e.poke(0xBF, c)
    nd = 0
    for i, r in enumerate(rows[1:]):
        f = 16683 + i
        e.step(r); m = e.ram(0x2A, 1)[0]; ram = e.ram(0x51, 2)
        s = e.state()
        X = ram[1]*256 + ram[0] + s['x']
        mine = [str(X), str(s['y']), str(s['hp']), str(m), str(s['ninpo'])]
        if f in M and mine[:3] != M[f][:3] or (f in M and mine[3] != M[f][3]):
            print(f, 'row', '+'.join(r) or '-', 'NesHawk X y hp pad np', mine, 'Mesen', M[f]); nd += 1
            if nd > 8: break
    print('done', f)
finally:
    e.close()
