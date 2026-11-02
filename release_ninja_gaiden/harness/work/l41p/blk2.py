"""15700-block high route without the type-8 bird hit (Mesen, record='last').
Phase 1 (to frame 15700): from the r2c state at K0, Right + jump A at j held h + optional B (2 f) at k.
  keep candidates with hp 16 and Ryu standing/running on the middle block (y 96); score X at 15700 (r2c 1709, hp 15).
Phase 2: best phase-1 lines + Right, A at j2 held h2 (+ optional blank frame before) -> X at 15790 with y 128 (TAS 1849? r2c ~1829).
python work/l41p/blk2.py"""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
K0 = 15585
fc.run_batch('s', [pads[:K0 - 14569]], record='last', keep=True, prefix='k'); fc._ka_slot = 'k1'
R, A_, B_ = 1, 128, 64
def X(m): return m[0x52]*256 + m[0x51] + m[0x86]
def mk(n, presses):
    p = [R] * n
    for f0, h, bit in presses:
        for f in range(f0, f0 + h): p[f - K0 - 1] |= bit
    return p
def runall(cands):
    out = []
    for i in range(0, len(cands), 40):
        out += [r.ram for r in fc.run_batch('k1', [bytes(c) for c in cands[i:i+40]], record='last', record_ram=True)]
    return out
t = time.time()
N1 = 15700 - K0
c1 = []; m1 = []
for j in range(15588, 15613):
    for h in (2, 4, 8, 14, 22):
        for k in [0] + list(range(j + 6, min(j + 62, 15695), 3)):
            pr = [(j, h, A_)] + ([(k, 2, B_)] if k else [])
            c1.append(mk(N1, pr)); m1.append(pr)
print('phase1', len(c1), flush=True)
rams = runall(c1)
ok = []
for pr, m in zip(m1, rams):
    if m[0x65] == 16 and m[0x8A] == 96 and m[0x6E] == 13:
        ok.append((X(m), m[0x64], pr))
ok.sort(key=lambda v: (-v[0], -v[1]))
print('time', round(time.time() - t), 'ok', len(ok), flush=True)
for v in ok[:15]: print('p1', v, flush=True)
N2 = 15790 - K0
c2 = []; m2 = []
seen = set()
for x, np_, pr in ok[:12]:
    if (x, np_) in seen and len(seen) > 6: continue
    seen.add((x, np_))
    for j2 in range(15700, 15745):
        for h2 in (2, 4, 8, 14):
            for gap in (0, 1):
                p = mk(N2, pr + [(j2, h2, A_)])
                if gap: p[j2 - 1 - K0 - 1] = 0
                c2.append(p); m2.append(pr + [(j2, h2, A_, gap)])
print('phase2', len(c2), flush=True)
rams = runall(c2)
res = sorted(((X(m), m[0x8A], m[0x65], m[0x64], pr) for pr, m in zip(m2, rams) if m[0x65] >= 16 and m[0x6E] == 13), key=lambda v: -v[0])
print('time', round(time.time() - t), flush=True)
for v in res[:15]: print('p2', v, flush=True)
fc.close()
