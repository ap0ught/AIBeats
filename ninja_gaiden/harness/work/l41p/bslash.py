"""For every spawn BF b: r2c pads with the tosser slash at k (orig 15077, or moved to 15066..15074), checked at 15300
(X 1130 y 48 J&S hp 16, tosser gone = the base). $BF poked at the r2c state 15000 (spawn at 15017: b = BF15000 + 17).
python work/l41p/bslash.py"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytearray(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
S = 15000
fc.run_batch('s', [bytes(pads[:S - 14569])], record='last', keep=True, prefix='k'); fc._ka_slot = 'k1'; fc.load('k1'); fc.save('base')
KS = [15077, 15066, 15068, 15070, 15072, 15074]
cands = []
for k in KS:
    p = bytearray(pads[S - 14569:15300 - 14569])
    for f in (15077, 15078): p[f - S - 1] &= ~64
    for f in (k, k + 1): p[f - S - 1] |= 64
    cands.append(bytes(p))
def ok(q):
    X = q[0x52]*256 + q[0x51] + q[0x86]
    toss = any(q[0x73] >> j & 1 and q[0x400 + j] == 2 for j in range(8))
    return X == 1130 and q[0x8A] == 48 and q[0xC9] == 133 and q[0x65] == 16 and not toss
for b in range(256):
    fc.load('base'); fc.poke(0xBF, (b - 17) & 255); fc.save('p'); fc._ka_slot = 'p'
    rs = fc.run_batch('p', cands, record='last', record_ram=True)
    print(b, ' '.join(f"{k}:{'ok' if ok(r.ram) else '--'}" for k, r in zip(KS, rs)), flush=True)
fc.close()
