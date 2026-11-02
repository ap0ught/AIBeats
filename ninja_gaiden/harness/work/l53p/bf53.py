"""5-3 thrower (type 2) vs $BF. From the TAS state F0 with $BF poked to v (all 256), play the TAS pad bytes to F1:
hp at F1, first divergence vs the TAS, axe (type 18) appearance frames, room at F1.
spawn BF = (v + FS - F0) mod 256 (FS = the TAS's thrower spawn frame).
python work/l53p/bf53.py F0 F1 FS [--rows file] [--step 1]"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
RF = ''; STEP = 1
if '--rows' in a: i = a.index('--rows'); RF = a[i+1]; del a[i:i+2]
if '--step' in a: i = a.index('--step'); STEP = int(a[i+1]); del a[i:i+2]
F0, F1, FS = int(a[0]), int(a[1]), int(a[2])
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
if RF: rows = [row(l.strip()) for l in open(RF) if l.strip() and not l.startswith('#')][:F1 - F0]
else: rows = [TM(g)[0x2A] for g in range(F0 + 1, F1 + 1)]
for v0 in range(0, 256, 32):
    vs = list(range(v0, v0 + 32, STEP))
    for v in vs:
        fc.load('b'); fc.poke(0xBF, v); fc.save(f'p{v}')
    rr = [fc.run_batch(f'p{v}', [rows], record='all')[0] for v in vs]
    for v, r in zip(vs, rr):
        st = r.states; div = None; throws = []; hits = []
        for i, s in enumerate(st):
            f = F0 + 1 + i
            if div is None and RXY(s) != tas_xy(f) and not RF: div = f
            if i and s['hp65'] < st[i-1]['hp65']: hits.append(f)
            for j in range(8):
                if s[f't{j}'] == 18 and (i == 0 or st[i-1][f't{j}'] != 18): throws.append(f)
        hp = st[-1]['hp65']; sp = (v + FS - F0) % 256
        print(f'v {v:3d} spawnBF {sp:3d} hp {hp} rm {st[-1]["room6e"]} X,y {RXY(st[-1])} div {div} hits {hits[:3]} axes {throws[:4]}', flush=True)
    for v in vs: fc.drop(f'p{v}')
fc.close()
