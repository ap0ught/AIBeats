"""Mesen TAS 5-3 states from l52p_tas26607.mst + NesHawk pad bytes; compare vs the dumps (tas53_ram.bin)."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core('states/mesen/l52p_tas26607.mst'); f = 26607
def pad(g): return TM(g)[0x2A]
CK = [26608, 26640, 26680, 26700, 26750, 26800, 26850, 26900, 26936, 26960, 26978, 26994, 27012, 27036, 27060, 27100, 27150,
      27200, 27250, 27300, 27350, 27400, 27450, 27484, 27508, 27560, 27600, 27650, 27700, 27750, 27800, 27850, 27880, 27900,
      27920, 27944, 27970, 28010, 28050, 28100, 28150, 28200, 28250, 28300, 28350, 28393, 28417, 28450, 28480, 28500, 28540,
      28560, 28580, 28600, 28628, 28652, 28680, 28720, 28760, 28800, 28843, 28867, 28950, 29050, 29099]
for ck in CK:
    fc.step([pad(g) for g in range(f + 1, ck + 1)], record='last'); f = ck
    r = fc.ram(); n = TM(ck)
    diff = [hex(a) for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    print(ck, 'diffs', len(diff), diff[:8], 'X,y', XY(r), 'hp', r[0x65], 'BF', r[0xBF], flush=True)
    fc.save('c'); fc.save_file('c', tas_mst(ck), frame=ck)
fc.close()
