import sys; sys.path.insert(0, 'work/l51a')
import rep as RP
from rep import *
RP.BIRD = (23290, 23350, 1090, 1190)
T0, END = 22596, 22830
KR = {'A': [{'A', 'Right'}], 'B': [{'B', 'Right'}], 'L': [{'Left'}, {'Left'}], '-': [set(), set()], 'BL': [{'B', 'Left'}, {'B', 'Left'}]}
def ov_of(evs):
    o = {t: {'Right'} for t in range(T0, END + 1)}
    for t, k in sorted(evs):
        for i, w in enumerate(KR[k]): o[t + i] = set(w)
    return o
base = [(22625,'A'),(22647,'A'),(22655,'B'),(22683,'B'),(22690,'A'),(22697,'L'),(22718,'B'),(22733,'A'),(22755,'B'),(22777,'A'),(22793,'L')]
R = Rep('work/l51a/p23100.txt', 472, 505, END)
for drop in (None, (22683,'B'), (22697,'L')):
    for t in range(22660, 22712, 1):
        for k in ('B',):
            evs = [e for e in base if e != drop] + [(t, k)]
            r = R.run(ov_of(evs))
            if r['bird']: print(drop, t, k, r, flush=True)
print('done')
