"""Mesen TAS 5-2 states from l51p_tas24147.mst + NesHawk pad bytes; compare vs the dumps."""
import sys
sys.path.insert(0, 'work/l52p')
from lib import *
fc = core('states/mesen/l51p_tas24147.mst'); f = 24147
def pad(g): return TM(g)[0x2A]
CK = [24300, 24426, 24427, 24470, 24520, 24560, 24600, 24620, 24640, 24662, 24700, 24760, 24800, 24812, 24820, 24874, 24896,
      24940, 25000, 25100, 25200, 25300, 25360, 25383, 25420, 25500, 25600, 25700, 25800, 25817, 25840, 25900, 25950, 26000,
      26050, 26100, 26200, 26300, 26328, 26600, 26607]
for ck in CK:
    fc.step([pad(g) for g in range(f + 1, ck + 1)], record='last'); f = ck
    r = fc.ram(); n = TM(ck)
    diff = [hex(a) for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    print(ck, 'diffs', len(diff), diff[:8], 'X,y', XY(r), 'hp', r[0x65], 'BF', r[0xBF], flush=True)
    fc.save('c'); fc.save_file('c', tas_mst(ck), frame=ck)
fc.close()
