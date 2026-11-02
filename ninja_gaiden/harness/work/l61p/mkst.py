"""Mesen TAS Act-6 states from l53p_tas29099.mst + NesHawk pad bytes; compare vs the dumps (tas61_ram.bin)."""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
fc = core('states/mesen/l53p_tas29099.mst'); f = 29099
KEY = [29258, 29259, 29313, 29314, 29900, 29907, 29908, 29911, 30000, 30062, 30063, 31000, 31010, 31486, 31487, 31636, 31637, 31638,
       31700, 31750, 31940, 32570, 32572, 32573, 32595, 33169, 33170, 33190, 33267, 33268, 33290, 33711, 33712, 33732, 34409, 34410, 34559, 34560]
CK = sorted(set(KEY + list(range(29300, 34561, 100)) + list(range(30050, 31640, 50))))
for ck in CK:
    fc.step([pad(g) for g in range(f + 1, ck + 1)], record='last'); f = ck
    r = fc.ram(); n = TM(ck)
    diff = [hex(a) for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    if diff and ck >= 29911 and ck <= 30062:
        for a in diff: fc.poke(int(a, 16), n[int(a, 16)])
        r = fc.ram(); print(ck, 'resynced (Mesen step() is 1 frame off in the act-end cutscene)', diff, flush=True)
        diff = [hex(a) for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    print(ck, 'diffs', len(diff), diff[:8], 'X,y', XY(r), 'hp', r[0x65], 'BF', r[0xBF], 'st', r[0x6D], flush=True)
    fc.save('c'); fc.save_file('c', tas_mst(ck), frame=ck)
fc.close()
