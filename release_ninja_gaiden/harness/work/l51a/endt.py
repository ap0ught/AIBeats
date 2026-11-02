"""End segment test on TAS states: legal TAS rows from TAS state S to the trigger, with BF poked for lag L (BF += L-504)."""
import sys; sys.path.insert(0, 'work/l51p')
from lib import *
S = int(sys.argv[1])
for L in [int(x) for x in sys.argv[2].split(',')]:
    fc = core(tas_mst(S)); r = fc.ram(); fc.poke(0xBF, (r[0xBF] + L - 504) % 256)
    hist0 = [T(f) for f in range(S - 60, S + 1)]
    rows = legalize_tas(S + 1, 24150, hist0)
    _, recs, _ = fc.step(rows, record='all'); fc.close()
    hp = recs[0]['hp65']; ev = []
    trig = None
    for i, s in enumerate(recs):
        f = S + 1 + i
        if s['hp65'] != hp: ev.append((f, RXY(s), hp, s['hp65'])); hp = s['hp65']
        if trig is None and s['e5c'] == 0: trig = f
    X, y = RXY(recs[-1])
    print('lag', L, 'hits', ev, 'trigger', trig, 'end', X, y, flush=True)
