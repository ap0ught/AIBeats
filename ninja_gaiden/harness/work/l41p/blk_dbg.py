import sys, collections
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
K0 = 15585
fc.run_batch('s', [pads[:K0 - 14569]], record='last', keep=True, prefix='k'); fc._ka_slot = 'k1'
def X(m): return m[0x52]*256 + m[0x51] + m[0x86]
N1 = 15700 - K0
# r2c itself from K0
r = fc.run_batch('k1', [pads[K0 - 14569:15700 - 14569]], record='last', record_ram=True)[0].ram
print('r2c at 15700', X(r), r[0x8A], r[0x65])
cands = []; meta = []
for j in range(15588, 15613, 3):
    for h in (2, 8, 22):
        for k in [0, j + 15, j + 30]:
            p = [1] * N1
            for f in range(j, j + h): p[f - K0 - 1] |= 128
            if k:
                for f in (k, k + 1): p[f - K0 - 1] |= 64
            cands.append(bytes(p)); meta.append((j, h, k))
rs = fc.run_batch('k1', cands, record='last', record_ram=True)
for m, rr in zip(meta, rs):
    q = rr.ram; print(m, X(q), q[0x8A], q[0x65], q[0x64], q[0x80])
fc.close()
