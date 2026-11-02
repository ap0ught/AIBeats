"""r2c 15700-block bird (type 8, hits r2c at 15631): try B / Down+B held 2 frames at frame j (Mesen, r2c NesHawk pads).
Report hit, first frame at X >= 1700 with y <= 96, ninpo."""
import sys
sys.path.insert(0, '.')
from ng import fastcore as F
from ng.solve import common as C
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytearray(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read())
K0 = 15560
fc.load('s'); fc.run_batch('s', [bytes(pads[:K0 - 14569])], record='last', keep=True, prefix='k')
# state at K0 kept in slot k1
def test(mods, n=200):
    p = bytearray(pads[K0 - 14569:K0 - 14569 + n])
    for f, m in mods: p[f - K0 - 1] |= m
    st = fc.run_batch('k1', [bytes(p)], record='all')[0].states
    hit = next((K0 + 1 + i for i, s in enumerate(st) if s['hp'] < 16), None)
    x17 = next((K0 + 1 + i for i, s in enumerate(st) if C.abs_x(s) >= 1700 and s['y'] <= 96), None)
    x18 = next((K0 + 1 + i for i, s in enumerate(st) if C.abs_x(s) >= 1740), None)
    return hit, x17, x18, st[-1]['ninpo']
print('base', test([]))
mB = F.to_mask(('B',)); mD = F.to_mask(('Down', 'B'))
for name, m in (('B', mB), ('Down+B', mD)):
    for j in range(15598, 15632):
        print(name, j, test([(j, m), (j + 1, m)]), flush=True)
fc.close()
