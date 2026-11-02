"""Room-36 jetpack-ninja gate vs $BF: from TAS state F0 (default 32300) with $BF poked to v (all 256), J&S rows
(work/l61p/js_30063_32595.txt) with the 32428 spin (B+Left 2 f) moved to row S (variants), to 32595. Reports hp hits, room-37 frame, item, np.
spawn-time $BF of the TAS = TM(F0)[BF] -> c-equivalent: c = (v - TM(F0)[BF] + 84) mod 256 (c = $BF on the 6-1 control row).
python work/l61p/sp36.py S1,S2,... [--f0 32300] [--vs a,b]"""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
F0 = opt('--f0', 32300); VS = opt('--vs', '')
SS = [int(x) for x in a[0].split(',')]
base = [row(l.strip()) for l in open('work/l61p/js_30063_32595.txt') if l.strip() and not l.startswith('#')]
def rows_for(S):
    r = list(base)
    for f in (32428, 32429): r[f - 30063] = ('Left',)
    if S:
        for f in (S, S + 1): r[f - 30063] = ('B', 'Left')
    return r[F0 + 1 - 30063: 32595 - 30063 + 1]
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
bf0 = TM(F0)[0xBF]
vs = [int(x) for x in VS.split(',')] if VS else list(range(256))
for S in SS:
    rows = rows_for(S)
    good = []; bad = []
    for k0 in range(0, len(vs), 64):
        ch = vs[k0:k0+64]
        for v in ch: fc.load('b'); fc.poke(0xBF, v); fc.save(f'p{v}')
        for v in ch:
            r = fc.run_batch(f'p{v}', [rows], record='all')[0]; st = r.states
            hits = [F0 + 1 + i for i in range(1, len(st)) if st[i]['hp65'] < st[i-1]['hp65']]
            rm37 = next((F0 + 1 + i for i, s in enumerate(st) if s['room6e'] == 37), None)
            c = (v - bf0 + 84) % 256
            ok = rm37 == 32573 and hits == [32560] and st[-1]['item'] == 133
            (good if ok else bad).append(c)
            if not ok: print(f'S {S} c {c} hits {hits[:3]} rm37 {rm37} it {st[-1]["item"]} np {st[-1]["np64"]}', flush=True)
            fc.drop(f'p{v}')
    print(f'S {S}: good {len(good)} bad {len(bad)} badc {sorted(bad)}', flush=True)
fc.close()
