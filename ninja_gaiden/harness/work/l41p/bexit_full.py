"""Full line: r2c pads with the block exit 15719..K replaced by a legal 2-frame Left+A at 15719-20 + Right, then r2c pads
from K+1 (K in a few values). Mesen."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytearray(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
for K in (15760, 15770, 15778, 15779, 15790, 15800):
    p = bytearray(pads)
    for f in range(15719, K + 1): p[f - 14570] = 1
    for f in (15719, 15720): p[f - 14570] = 130
    st = fc.run_batch('s', [bytes(p)], record='all', stops=[(0x6D, 'changed', 0)])[0].states
    hits = [(14570 + i, s['hp']) for i, s in enumerate(st) if i and s['hp'] < st[i-1]['hp']]
    r14 = next((14570 + i for i, s in enumerate(st) if s['room'] == 14), None)
    r15 = next((14570 + i for i, s in enumerate(st) if s['room'] == 15), None)
    print('K', K, 'r14', r14, 'r15', r15, 'end', 14569 + len(st), 'stage', st[-1]['stage'], 'hits', hits, 'np', st[-1]['ninpo'], 'item', st[-1]['item'], flush=True)
fc.close()
