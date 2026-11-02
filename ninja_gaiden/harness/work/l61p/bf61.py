"""Act-6 arrival scan: from the TAS state F0 with $BF poked to v (all 256, or --vs list), play rows (default: the legalized
TAS rows work/l61p/leg_30063_32600.txt from 30063) to F1. Per v: c = $BF on the 6-1 control row (= v + 1 + 30062 - F0 ... printed),
first divergence vs the TAS, hp hits, axe (type 18) appearances, thrower (type 2) spawns, room at F1 and the frame of each room change.
python work/l61p/bf61.py F0 F1 [--rows file --rows0 first_row_frame] [--vs a,b,c] [--junk seed]"""
import sys, random
sys.path.insert(0, 'work/l61p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
RF = opt('--rows', 'work/l61p/leg_30063_32600.txt'); R0 = opt('--rows0', 30063); VS = opt('--vs', ''); JS = opt('--junk', -1)
F0, F1 = int(a[0]), int(a[1])
allrows = [row(l.strip()) for l in open(RF) if l.strip() and not l.startswith('#')]
rows = allrows[F0 + 1 - R0: F1 + 1 - R0]
assert len(rows) == F1 - F0, (len(rows), F1 - F0)
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
bf0 = fc.ram()[0xBF]
vs_all = [int(x) for x in VS.split(',')] if VS else list(range(256))
for k0 in range(0, len(vs_all), 32):
    vs = vs_all[k0:k0 + 32]
    for v in vs:
        fc.load('b'); fc.poke(0xBF, v)
        if JS >= 0:
            rng = random.Random(JS * 1000 + v)
            for ad in range(0x400, 0x4A8): fc.poke(ad, rng.randrange(256))
        fc.save(f'p{v}')
    rr = [fc.run_batch(f'p{v}', [rows], record='all')[0] for v in vs]
    for v, r in zip(vs, rr):
        st = r.states; div = None; axes = []; hits = []; rooms = []; thr = []
        for i, s in enumerate(st):
            f = F0 + 1 + i
            if div is None and RXY(s) != tas_xy(f): div = f
            if i and s['hp65'] < st[i-1]['hp65']: hits.append(f)
            if i and s['room6e'] != st[i-1]['room6e']: rooms.append(f)
            for j in range(8):
                if s[f't{j}'] == 18 and (i == 0 or st[i-1][f't{j}'] != 18): axes.append(f)
                if s[f't{j}'] == 2 and (i == 0 or st[i-1][f't{j}'] != 2): thr.append(f)
        print(f'v {v:3d} (TAS {bf0}) shift {(v - bf0) % 256:3d} hp {st[-1]["hp65"]} np {st[-1]["np64"]} it {st[-1]["item"]} rm {st[-1]["room6e"]} X,y {RXY(st[-1])} div {div} hits {hits[:4]} rooms {rooms} axes {axes[:6]} thr {thr[:4]}', flush=True)
    for v in vs: fc.drop(f'p{v}')
fc.close()
