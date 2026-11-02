"""Grid over the three jump shifts + the air turn; full range with bird/hit/np constraints; score X at our 23,580."""
import sys, itertools; sys.path.insert(0, 'work/l51a')
import rep as RP
from rep import *
RP.BIRD = (23280, 23380, 1100, 1200); RP.SF = 23580
T0, END = 22596, 23095
KR = {'A': [{'A', 'Right'}], 'B': [{'B', 'Right'}], 'L': [{'Left'}, {'Left'}], '-': [set(), set()], 'BL': [{'B', 'Left'}, {'B', 'Left'}]}
def ov_of(evs):
    o = {t: {'Right'} for t in range(T0, END + 1)}
    for t, k in sorted(evs):
        for i, w in enumerate(KR[k]): o[t + i] = set(w)
    return o
fixed = [(22625,'A'),(22655,'B'),(22683,'B'),(22718,'B'),(22755,'B'),(22777,'A'),(22796,'L'),(22851,'A'),(22870,'B'),(22890,'B'),(22950,'A'),(22998,'B'),(23011,'A'),(23053,'B'),(23059,'A'),(23061,'B')]
R = Rep('work/l51a/p23100.txt', 472, 505, END)
res = []
D = [int(x) for x in sys.argv[1].split(',')]
for d1 in D:
    for d2 in range(-1, 5):
        for d3 in range(-1, 5):
            for tl in [None] + list(range(22694, 22702)):
                evs = fixed + [(22644 + d1, 'A'), (22687 + d2, 'A'), (22730 + d3, 'A')] + ([(tl, 'L')] if tl else [])
                r = R.run(ov_of(evs))
                ok = r['dead'] is None and r['bird'] and r['last'][4] >= 30 and r['last'][5] == 130 and any(23578 <= h[0] <= 23600 for h in r['hits']) and all(h[0] >= 23578 for h in r['hits'])
                if ok:
                    print('OK', d1, d2, d3, tl, 'X@23580', r['sfx'], 'hits', r['hits'], flush=True)
                    res.append((r['sfx'], d1, d2, d3, tl))
res.sort(reverse=True); print('BEST', res[:10])
