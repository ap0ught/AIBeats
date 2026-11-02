"""Mesen TAS states at 4-4 pre-control (21,352) and control (21,353) from l43p_tas21060.mst + TAS pads; check vs NesHawk RAM dump."""
import sys
sys.path.insert(0, 'work/l44p')
from lib import *
d = open('work/l43p/tas43_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
pad = lambda f: d[(f - f0 - 1) * 2048 + 0x2A]
NR = lambda f: d[(f - f0 - 1) * 2048:(f - f0) * 2048]
fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD)
fc.put('s', open('states/mesen/l43p_tas21060.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
def show(tag, r):
    print(tag, 'x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF], '62', r[0x62], '63', r[0x63],
          'st', r[0x6D], 'rm', r[0x6E], 'bhp', r[0x66], 'en', hex(r[0x73]), flush=True)
f = 21060
for ck in (21352, 21353, 21376, 21420):
    fc.step(bytes(pad(g) for g in range(f + 1, ck + 1)), record='last'); f = ck
    r = fc.ram(); n = NR(ck)
    diff = [hex(a) for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    show(f'{ck} diffs {len(diff)} {diff[:8]}', r)
    if ck in (21352, 21353):
        fc.save('c'); fc.save_file('c', f'states/mesen/l44p_tas{ck}.mst', frame=ck)
# continue with raw TAS rows to the 5-1 control
st_prev = None
for g in range(21421, 22130):
    fc.step([T(g)], record='last'); r = fc.ram()
    if r[0x6D] != st_prev or g in (21971, 21972, 21973, 22123, 22124, 22125):
        show(f'{g}', r); st_prev = r[0x6D]
fc.close()
