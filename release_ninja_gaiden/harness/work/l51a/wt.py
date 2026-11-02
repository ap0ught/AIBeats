"""Wall test: f1 events with the wall-bird turn L at tL, later TAS events shifted by sh; full range to TAS END (lag 505 axis)."""
import sys; sys.path.insert(0, 'work/l51a')
import rep as RP
from rep import *
RP.BIRD = (23280, 23380, 1100, 1200)
T0, END = 22596, int(sys.argv[1]) if len(sys.argv) > 1 else 23110
KR = {'A': [{'A', 'Right'}], 'B': [{'B', 'Right'}], 'L': [{'Left'}, {'Left'}], '-': [set(), set()], 'BL': [{'B', 'Left'}, {'B', 'Left'}]}
def ov_of(evs):
    o = {t: {'Right'} for t in range(T0, END + 1)}
    for t, k in sorted(evs):
        for i, w in enumerate(KR[k]): o[t + i] = set(w)
    return o
f1 = [(22625,'A'),(22647,'A'),(22655,'B'),(22683,'B'),(22690,'A'),(22697,'L'),(22718,'B'),(22733,'A'),(22755,'B'),(22777,'A')]
later = [(22848,'A'),(22867,'B'),(22887,'B'),(22947,'A'),(22995,'B'),(23008,'A'),(23050,'B'),(23056,'A'),(23058,'B')]
R = Rep('work/l51a/p23100.txt', 472, 505, END)
for tL in (22796, 22797, 22800, 22801, 22804, 22805, 22806):
    for sh in (3, 4, 5):
        evs = f1 + [(tL, 'L')] + [(t + sh, k) for t, k in later]
        r = R.run(ov_of(evs))
        print(tL, sh, 'bird', r['bird'], 'hits', r['hits'], 'dead', r['dead'], 'last', r['last'], flush=True)
