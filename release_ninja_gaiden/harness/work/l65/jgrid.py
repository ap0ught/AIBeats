"""Heart-jump grid (Mesen): from a rows prefix (row 1 = 6-5 control row) and bf, try one jump step per candidate:
w rows of pd (R/-/L), jump (A 2 rows), Right on ALL rows for t < kR, nothing for kR <= t < kL, Left for t >= kL (no slash from kL on),
slash cycle Down|Down+B|B|-|- from row o of the jump. Reports per candidate: heart hits, hp lost, landing row/X (Ryu's $84 bit 2 clear).
python work/l65/jgrid.py <prefix rows file> <bf> [--top 20] [--ws R0..] [--out best.txt]"""
import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
TOP = int(opt('--top', '25')); WS = opt('--ws', '-0,R1,R2,R3,R4,R5,R6,L1,L2,L3,-2,-4,-6,-8,-10').split(',')
R0S = [int(x) for x in opt('--r0', '0').split(',')]
KRS = [int(x) for x in opt('--kr', '0,4,8,12,16,20,24,30').split(',')]
KLS = [int(x) for x in opt('--kl', '24,28,32,36,99').split(',')]
OUT = opt('--out', '')
pre = rows_of(a[0]); bf = int(a[1])
HIST = [()] * 150
D = {'-': (), 'R': ('Right',), 'L': ('Left',)}
def cand(w, kR, kL, o, n=60, r0=0):
    rr = [D[w[0]]] * int(w[1:])
    for t in range(n):
        r = set()
        if t < 2: r.add('A')
        if t >= kL: r.add('Left')
        else:
            if r0 <= t < kR: r.add('Right')
            k = t - o
            if k >= 0:
                ph = k % 5
                if ph == 0: r.add('Down')
                elif ph == 1: r |= {'Down', 'B'}
                elif ph == 2: r.add('B')
        rr.append(tuple(sorted(r)))
    return rr
L0 = K.Legal(HIST + pre)
fc = core65(bf)
fc.step(pre); fc.save('s0')
s0 = fc.ram()
cs = []
for w in WS:
  for r0 in R0S:
    for kR in KRS:
        for kL in KLS:
            if kL <= kR and kL != 99: continue
            if kR and kR <= r0: continue
            for o in range(5):
                rr = cand(w, kR, kL, o, r0=r0)
                Lx = L0.copy(); n = 0
                for r in rr:
                    if Lx.why(r): break
                    Lx.push(r); n += 1
                if n < int(w[1:]) + 30: continue
                cs.append(((w, r0, kR, kL, o), rr[:n]))
res = fc.run_batch('s0', [c[1] for c in cs], record='all', stops=[(0x66, '==', 0), (0x65, '==', 0)])
out = []
hp0 = s0[0x65]; h0 = s0[0x66]
for (sp, rr), r in zip(cs, res):
    st = r.states
    w = int(sp[0][1:])
    air = next((i for i in range(w, len(st)) if st[i]['rf84'] & 4), None)
    if air is None: continue
    land = next((i for i in range(air + 3, len(st)) if not (st[i]['rf84'] & 4)), None)
    if land is None: continue
    hits = h0 - st[land]['boss']
    hpl = hp0 - min(s['hp65'] for s in st[:min(len(st), land + 8)])
    out.append((-hits, hpl, land + 1, sp, st[land]['x86'], st[land]['y8a'], rr[:land + 1]))
out.sort(key=lambda q: (q[1] > 0, q[0] * 6 + q[2]))
print('max hits any', min(q[0] for q in out), 'with no damage', min([q[0] for q in out if q[1] == 0] or [0]))
for q in sorted(out, key=lambda q: q[0])[:8]: print('  ', -q[0], q[1], q[3], q[4], q[2])
print('bf', bf, 'prefix', len(pre), 'start X', s0[0x86], 'heart', h0, 'hp', hp0, 'cands', len(cs))
for q in out[:TOP]:
    print('hits', -q[0], 'hplost', q[1], 'land row', len(pre) + q[2], 'spec', q[3], 'X', q[4], 'y', q[5])
if OUT and out:
    q = out[0]
    with open(OUT, 'w', newline='\n') as f:
        f.write(f'# jgrid best: spec {q[3]} hits {-q[0]} land row {len(pre) + q[2]}\n')
        for r in pre + q[6]: f.write(('+'.join(r) if r else '') + '\n')
fc.close()
