"""l53a: run a base rows file (from 26608; TAS state 26607 + pokes) with many override sets, report legality, np/hp events,
X at frame --at, room-28 frame. python work/l53a/ovr.py base.txt --at 26900 'f1=Row;f2=Row' 'f1-f3=Row' ...
   a spec 'grid:F0-F1:ROW1/ROW2:len' = for each start f in F0..F1 and each ROW, rows f..f+len-1 = ROW."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
AT = opt('--at', 26900); POKES = opt('--poke', '65=12'); PAD = opt('--pad', 60)
base = [row(l.strip()) for l in open(a[0]) if l.strip() and not l.startswith('#')]
specs = []
for sp in a[1:]:
    if sp.startswith('grid:'):
        _, fr, rr, ln = sp.split(':'); f0, f1 = map(int, fr.split('-'))
        for f in range(f0, f1 + 1):
            for r in rr.split('/'): specs.append(f'{f}-{f+int(ln)-1}={r}')
    else: specs.append(sp)
hist = [T(f) for f in range(26458, 26608)]
hist = [tuple(sorted(set(r) - ({'Left'} if {'Left','Right'} <= set(r) else set()) - ({'Up','Down'} if {'Up','Down'} <= set(r) else set()))) for r in hist]
fc = core(tas_mst(26607))
for p in [q for q in POKES.split(',') if q]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
fc.save('b'); fc._ka_slot = 'b'
cands = []
for sp in ['base'] + specs:
    rows = list(base) + [()] * PAD
    if sp != 'base':
        for part in sp.split(';'):
            k, v = part.split('=')
            x, y = (map(int, k.split('-')) if '-' in k else (int(k), int(k)))
            for f in range(x, y + 1): rows[f - 26608] = row(v)
    cands.append((sp, rows))
for i in range(0, len(cands), 40):
    rr = fc.run_batch('b', [c[1] for c in cands[i:i+40]], record='all')
    for (sp, rows), r in zip(cands[i:i+40], rr):
        lg = legal_ok(rows[:len(base)], hist)
        ev = []; prev = None; xat = None; r28 = None
        for j, s in enumerate(r.states):
            f = 26608 + j
            if prev:
                for k in ('hp65', 'np64'):
                    if s[k] != prev[k]: ev.append(f'{f}:{k[:2]}{prev[k]}>{s[k]}')
                if s['room6e'] != prev['room6e'] and r28 is None: r28 = f
            if f == AT: xat = RXY(s)
            prev = s
        print(sp, '| legal', lg or 'ok', '| at', AT, xat, '| r28', r28, '|', ' '.join(ev), flush=True)
fc.close()
