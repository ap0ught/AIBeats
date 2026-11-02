"""Tosser repair grid for a bad spawn BF b (Mesen): r2c NesHawk pads with (i) w blank frames inserted at frame o,
and/or (ii) the B at 15077 moved to k. Score = first frame at X >= 1100 with J&S held (base 15280), hits.
python work/l41p/tfix.py b [b ...]"""
import sys, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
S = 15040; END = 15300
def P(f): return pads[f - 14570]
B = 64
def cand(o, w, k):
    out = []
    for f in range(S + 1, END + 1):
        p = P(f)
        if f in (15077, 15078) and k: p &= ~B
        if k and f in (k, k + 1): p |= B
        if f == o: out += [0] * w
        out.append(p)
    return bytes(out)
for b in [int(v) for v in sys.argv[1:]]:
    fc.load('s'); fc.poke(0xBF, (b - 448) & 255); fc.save('p')
    fc.run_batch('p', [pads[:S - 14569]], record='last', keep=True, prefix='q'); fc._ka_slot = 'q1'
    cands = []; meta = []
    for o in range(S + 1, 15100, 2):
        for w in range(0, 21):
            if w == 0 and o > S + 1: continue
            cands.append(cand(o, w, 0)); meta.append((o, w, 0))
    for k in range(15062, 15100):
        for w in (0, 1, 2, 3, 4):
            cands.append(cand(S + 1, w, k)); meta.append((S + 1, w, k))
    res = []
    for i in range(0, len(cands), 40):
        for m, r in zip(meta[i:i+40], fc.run_batch('q1', cands[i:i+40], record='last', record_ram=True)):
            q = r.ram; Xe = q[0x52]*256 + q[0x51] + q[0x86]
            toss = any(q[0x73] >> j & 1 and q[0x400 + j] == 2 for j in range(8))
            if q[0xC9] == 133 and not toss: res.append((-Xe, -q[0x65], m, q[0x8A], q[0x64]))
    res.sort()
    print('spawnBF', b, 'n', len(cands), 'ok', len(res), 'best (-X@15300, -hp, (o,w,k), y, np):', res[:6], flush=True)
    fc._ka_slot = 's'
fc.close()
