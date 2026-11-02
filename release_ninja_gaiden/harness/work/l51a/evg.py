"""Evaluate climb-beam goals: prefix rows (to the beam start) + goal rows + legal TAS rows at lag (goal f - TAS ref +d).
python -u work/l51a/evg.py <prefix rows> <beam start f> <goals json> <TAS ref f> <TAS end> [drop23355]"""
import sys, json; sys.path.insert(0, 'work/l51a')
from rep import *
pre = rows_file(sys.argv[1]); F0 = int(sys.argv[2]); G = json.load(open(sys.argv[3])); TREF = int(sys.argv[4]); END = int(sys.argv[5])
drop = len(sys.argv) > 6 and sys.argv[6] == "1"
DS = [int(x) for x in sys.argv[7].split(",")] if len(sys.argv) > 7 else [0, 1]
pre = pre[:F0 - CTL + 1]
seen = set(); res = []
for g in G:
    gf, hp, np_, X, y, rws = g
    rows = [row(r) if r else () for r in rws]
    key = tuple(rows)
    if key in seen: continue
    seen.add(key)
    for d in DS:
        LG = gf - TREF + d
        R = Rep(pre + rows, len(pre) + len(rows), LG, END, {23355: {'Right'}, 23356: {'Right'}} if drop else {})
        r = R.run({}); R.fc.close()
        early = [h for h in r['hits'] if h[0] - LG < END]
        res.append((r['dead'] is None and not early, -(r['last'][1] if r['last'] else 0), gf, d, LG, r['hits'][:3], r['dead'], r['last']))
        print(gf, d, LG, 'hits', r['hits'][:3], 'dead', r['dead'], 'last', r['last'], flush=True)
res.sort(key=lambda q: (not q[0], q[2], q[1]))
print('BEST', res[:5])
