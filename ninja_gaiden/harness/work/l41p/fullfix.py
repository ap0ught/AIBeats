"""Full r2c line with the tosser slash (B on 15077-15078) moved to k,k+1, for spawn BF b (Mesen).
python work/l41p/fullfix.py b k [b k ...]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytearray(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
a = [int(v) for v in sys.argv[1:]]
for b, k in zip(a[::2], a[1::2]):
    p = bytearray(pads)
    for f in (15077, 15078): p[f - 14570] &= ~64
    for f in (k, k + 1): p[f - 14570] |= 64
    fc.load('s'); fc.poke(0xBF, (b - 448) & 255); fc.save('p')
    st = fc.run_batch('p', [bytes(p)], record='all', stops=[(0x6D, 'changed', 0)])[0].states
    hits = [(14570 + i, s['hp']) for i, s in enumerate(st) if i and s['hp'] < st[i-1]['hp']]
    r15 = next((14570 + i for i, s in enumerate(st) if s['room'] == 15), None)
    print('spawnBF', b, 'B at', k, 'room15', r15, 'end', 14569 + len(st), 'hits', hits, 'np', st[-1]['ninpo'], 'item', st[-1]['item'], flush=True)
fc.close()
