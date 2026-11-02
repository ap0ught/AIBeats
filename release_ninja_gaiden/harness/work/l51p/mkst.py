"""Mesen TAS 5-1 states from l44p_tas21353.mst + TAS rows (raw to 22,125, then the NesHawk pad bytes); compare vs tas51_ram.bin."""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
fc = core('states/mesen/l44p_tas21353.mst'); f = 21353
fc.step([T(g) for g in range(21354, 22125)], record='last'); f = 22124
fc.save('c'); fc.save_file('c', tas_mst(22124), frame=22124)
CK = [22125, 22200, 22280, 22300, 22340, 22360, 22400, 22500, 22600, 22700, 22780, 22820, 22900, 23000, 23050, 23100, 23200,
      23300, 23400, 23500, 23520, 23600, 23700, 23800, 23900, 24000, 24100, 24147]
for ck in CK:
    fc.step([T(g) if g == 22125 else TPAD[g] for g in range(f + 1, ck + 1)], record='last'); f = ck
    r = fc.ram()
    if ck > TF0:
        n = TM(ck); diff = [hex(a) for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    else: diff = ['?']
    print(ck, 'diffs', len(diff), diff[:8], 'X,y', XY(r), 'hp', r[0x65], 'BF', r[0xBF], flush=True)
    fc.save('c'); fc.save_file('c', tas_mst(ck), frame=ck)
fc.close()
