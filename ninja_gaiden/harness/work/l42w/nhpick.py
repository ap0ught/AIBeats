"""NesHawk-check the top wenum results: python -u work/l42w/nhpick.py <neshawk state> <top.json> [--n 15]
Prints, per candidate, the Mesen trigger and the NesHawk trigger / misreads; writes the best clean one to
<top.json minus _top.json>_nh.inputs.txt."""
import sys, json
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
from ng.inputs import to_mask
a = sys.argv[1:]
n = 15
if '--n' in a:
    i = a.index('--n'); n = int(a[i + 1]); del a[i:i + 2]
nhs, top = a
cands = json.load(open(top))[:n]
e = C.open_emu('l42w_nhpick.log')
best = None
try:
    e.tick(TICKS)
    for k, c in enumerate(cands):
        rows = [tuple(x for x in r.split('+') if x) for r in c['rows']]
        st = e.load(nhs); f0 = st['frame']
        _, rams = e.run_ram(rows)
        tn = next((f0 + 1 + i for i, m in enumerate(rams) if m[0x5C] == 0), None)
        mis = [f0 + 1 + i for i, m in enumerate(rams) if m[0x2A] != to_mask(rows[i])]
        hp = rams[-1][0x65]
        print(k, 'mesen', c['trigger'], 'hp', c['hp'], '| NH trigger', tn, 'hp', hp, 'misreads', mis[:6], c['params'], flush=True)
        if tn is not None and (best is None or (tn, -hp) < (best[0], -best[1])): best = (tn, hp, rows, c)
finally:
    e.close()
if best:
    out = top.replace('_top.json', '_nh.inputs.txt')
    C.write_inputs(out, best[2], f'nhpick {nhs}: NesHawk trigger {best[0]} hp {best[1]} params {best[3]["params"]}')
    print('BEST NH', best[0], 'hp', best[1], '->', out)
