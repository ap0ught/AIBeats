"""Legal (2-frame holds) replacements for r2c's conflict-dependent block exit (15725-15732), Mesen from the r2c state
at 15716 (pads). Rows: Right, except press P1 (dir1+A, 2 f) at k1 and optional P2 (dir2+A, 2 f) at k2 (>= k1+5),
optional blank frames before k1. Score: X at 15800 with y 128 on the ground, hp. r2c (with the conflict): see 'orig'.
python work/l41p/bexit.py"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytearray(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
S = 15716; E = 15800
fc.run_batch('s', [bytes(pads[:S - 14569])], record='last', keep=True, prefix='k'); fc._ka_slot = 'k1'
R, L, A = 1, 2, 128
def X(m): return m[0x52]*256 + m[0x51] + m[0x86]
orig = fc.run_batch('k1', [bytes(pads[S - 14569:E - 14569])], record='last', record_ram=True)[0].ram
print('orig', X(orig), orig[0x8A], orig[0x65], flush=True)
cands = []; meta = []
for k1 in range(15719, 15737):
    for d1 in (L, R, 0):
        for blank in (0, 2):
            for k2 in [0] + list(range(k1 + 5, k1 + 17)):
                for d2 in ((R,) if k2 else (None,)):
                    p = [R] * (E - S)
                    for f in range(k1 - blank, k1): p[f - S - 1] = 0
                    for f in (k1, k1 + 1): p[f - S - 1] = d1 | A
                    if k2:
                        for f in range(k1 + 2, k2): p[f - S - 1] = R if d2 == R else (R if d1 == R else 0)
                        for f in (k2, k2 + 1): p[f - S - 1] = d2 | A
                    cands.append(bytes(p)); meta.append((k1, d1, blank, k2, d2))
print('cands', len(cands), flush=True)
res = []
for i in range(0, len(cands), 60):
    for m, r in zip(meta[i:i+60], fc.run_batch('k1', cands[i:i+60], record='last', record_ram=True)):
        q = r.ram
        if q[0x8A] < 140 and q[0x6E] == 13: res.append((X(q), q[0x65], q[0x8A], m))
res.sort(key=lambda v: (-v[0], -v[1]))
for v in res[:12]: print(v, flush=True)
fc.close()
