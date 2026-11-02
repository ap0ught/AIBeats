"""5-3 head start: legalized TAS rows from the 5-3 control row 26608 (Left) to P, tested for arrival independence (Mesen):
from TAS state 26607 (before the control row) with pokes ($BF, invincibility $95, hp $65, ninpo $64, junk enemy slots
$400-$4A7), play the rows, compare Ryu X,y / hp / ninpo / item with the unpoked TAS run on every frame.
python work/l53p/pre53.py P [--rows file] [--out file]"""
import sys, random
sys.path.insert(0, 'work/l53p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
RF = opt('--rows', ''); OUT = opt('--out', '')
P = int(a[0])
hist = [tuple(sorted(set(T(f)) - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()) - ({'Up','Down'} if {'Up','Down'} <= set(T(f)) else set()))) for f in range(26608 - 150, 26608)]
if RF: rows = [row(l.strip()) for l in open(RF) if l.strip() and not l.startswith('#')]
else: rows = legalize_tas(26608, P, hist)
print('rows', len(rows), 'legal', legal_ok(rows, hist) or 'ok', flush=True)
NL = chr(10)
if OUT: open(OUT, 'w').write(f'# 5-3 stage rows from the control row (TAS 26608), legalized TAS rows to {P}' + NL + NL.join(('+'.join(sorted(r)) or '-') for r in rows) + NL)
fc = core(tas_mst(26607)) if os.path.exists(tas_mst(26607)) else core('states/mesen/l52p_tas26607.mst')
fc.save('b'); fc._ka_slot = 'b'
base = fc.run_batch('b', [rows], record='all')[0].states
def sig(s): return (RXY(s), s['hp65'], s['np64'], s['item'], s['room6e'])
rng = random.Random(53)
trials = []
for k in range(16):
    pk = {0xBF: (k * 37) % 256, 0x95: (0, 33, 60)[k % 3], 0x65: (3, 8, 12, 16)[k % 4], 0x64: (35, 40, 55)[k % 3]}
    junk = {ad: rng.randrange(256) for ad in range(0x400, 0x4A8)} if k % 2 else {}
    trials.append((pk, junk))
for pk, junk in trials:
    fc.load('b')
    for ad, v in {**junk, **pk}.items(): fc.poke(ad, v)
    fc.save('t')
    st = fc.run_batch('t', [rows], record='all')[0].states
    d = None
    for i, (s, b) in enumerate(zip(st, base)):
        if RXY(s) != RXY(b) or s['item'] != b['item'] or s['room6e'] != b['room6e'] or s['np64'] - pk[0x64] != b['np64'] - 40 or s['hp65'] - pk[0x65] != b['hp65'] - 3:
            d = (26608 + i, RXY(s), RXY(b), s['hp65'], s['np64']); break
    e = st[-1]
    print('poke', {hex(k): v for k, v in pk.items()}, 'junk' if junk else '', '| first diff', d, '| end', sig(e), flush=True)
print('base end', sig(base[-1]), 'TAS', tas_xy(26608 + len(rows) - 1))
fc.close()
