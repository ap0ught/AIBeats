import sys; sys.path.insert(0, 'work/l51a')
from rep import *
pf = sys.argv[1]; END = int(sys.argv[2]); Ns = range(int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])); LGs = [int(x) for x in sys.argv[6].split(',')]
for N in Ns:
    for LG in LGs:
        R = Rep(pf, N - CTL + 1, LG, END)
        r = R.run({}); R.fc.close()
        print(N, LG, r, flush=True)
