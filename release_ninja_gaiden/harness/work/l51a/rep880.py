import sys, itertools; sys.path.insert(0, 'work/l51a')
from rep import *
LG = int(sys.argv[1]); END = int(sys.argv[2])
R = Rep('work/l51a/p23100.txt', 472, LG, END)
res = []
# jump at 22,644 shifted by dj; slash 22,655 shifted by db (None = drop); extra B at eb
for dj in range(-4, 5):
    for db in list(range(-6, 8)) + [None]:
        ov = {22644: {'Right'}, 22645: {'Right'}, 22655: {'Right'}, 22656: {'Right'}}
        ov[22644 + dj] = {'A', 'Right'}
        if db is not None: ov[22655 + db] = {'B', 'Right'}
        r = R.run(ov)
        hitf = r['hit'][0] if r['hit'] else 99999
        res.append((-(r['last'][1] if not r['dead'] else 0), hitf, dj, db, r))
res.sort(key=lambda q: (q[4]['dead'] is not None, -q[1], q[0]))
for q in res[:15]: print(q[2], q[3], q[4], flush=True)
