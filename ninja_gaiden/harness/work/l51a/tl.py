"""Test the 22,793-type Left turn timing: events file + shift of the L event; prints spawn + scroll."""
import sys; sys.path.insert(0, 'work/l51a')
import rep as RP
from rep import *
RP.BIRD = (23280, 23380, 1100, 1200)
T0, END = 22596, 22830
KR = {'A': [{'A', 'Right'}], 'B': [{'B', 'Right'}], 'L': [{'Left'}, {'Left'}], '-': [set(), set()], 'BL': [{'B', 'Left'}, {'B', 'Left'}]}
def ov_of(evs):
    o = {t: {'Right'} for t in range(T0, END + 1)}
    for t, k in sorted(evs):
        for i, w in enumerate(KR[k]): o[t + i] = set(w)
    return o
base = [(int(t), k) for t, k in (x.split(':') for x in sys.argv[1].split(','))]
base = [e for e in base if e[0] <= END]
R = Rep('work/l51a/p23100.txt', 472, 505, END)
noL = [e for e in base if e != (22793, 'L')]
for t in [None] + list(range(22790, 22816)):
    evs = noL + ([(t, 'L')] if t else [])
    r = R.run(ov_of(evs))
    print(t, r, flush=True)
