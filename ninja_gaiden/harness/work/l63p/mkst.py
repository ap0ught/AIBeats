"""Mesen TAS states for 6-3 .. END from l61p_tas34560.mst + NesHawk pad bytes; compare vs the dumps (tas63_ram.bin)."""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
fc = core('states/mesen/l61p_tas34560.mst'); f = 34560
KEY = [34561, 34562, 34989, 34990, 35012, 35013, 35144, 35145, 35167, 35168, 36436, 36437, 36459, 36460, 37117, 37118, 37123, 37125, 37126, 37277, 37278,
       37338, 37339, 37932, 37934, 37935, 38086, 38087, 38187, 38188, 38778, 38780, 38781, 38932, 38933, 39083, 39084, 39300, 39525, 39530, 39600]
CK = sorted(set(KEY + list(range(34600, 39100, 100)) + list(range(34600, 37200, 50))))
RS = [(37118, 37278), (37339, 38087), (38188, 38933), (39084, 39700)]
for ck in CK:
    fc.step([pad(g) for g in range(f + 1, ck + 1)], record='last'); f = ck
    r = fc.ram(); n = TM(ck)
    diff = [a for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    if diff and any(a <= ck <= b for a, b in RS):
        for a in diff: fc.poke(a, n[a])
        print(ck, 'resynced', [hex(a) for a in diff], flush=True)
        r = fc.ram(); diff = [a for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    print(ck, 'diffs', len(diff), [hex(a) for a in diff[:8]], 'X,y', XY(r), 'hp', r[0x65], 'BF', r[0xBF], 'st', r[0x6D], 'rm', r[0x6E], 'boss', r[0x66], flush=True)
    fc.save('c'); fc.save_file('c', tas_mst(ck), frame=ck)
fc.close()
