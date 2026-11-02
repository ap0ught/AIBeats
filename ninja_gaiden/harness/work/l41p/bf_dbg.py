import sys
sys.path.insert(0, '.')
from ng import fastcore as F
from ng.solve import common as C
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytearray(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read())
K0 = 15560
r = fc.run_batch('s', [bytes(pads[:K0 - 14569])], record='last', keep=True, prefix='k')
print('K0 state', C.abs_x(r[0].states[-1]), r[0].states[-1]['y'], 'slot', r[0].slot if hasattr(r[0],'slot') else '?')
j = int(sys.argv[1]); m = F.to_mask(tuple(sys.argv[2].split('+')))
p = bytearray(pads[K0 - 14569:K0 - 14569 + 120])
if j: p[j - K0 - 1] |= m; p[j - K0] |= m
st = fc.run_batch('k1', [bytes(p)], record='all')[0].states
for i, s in enumerate(st):
    f = K0 + 1 + i
    if f % 3 == 0 or (j and abs(f - j) < 3): print(f, p[i], C.abs_x(s), s['y'], s['hp'], s['ninpo'], s['anim'])
fc.close()
