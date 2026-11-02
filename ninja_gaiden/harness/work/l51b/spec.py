"""spec string 'R:10 AL:2 ...' -> rows file: python work/l51b/spec.py 'spec' out.txt"""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
AB = {'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B'}
rows = []
for tok in sys.argv[1].split():
    k, n = tok.split(':'); r = () if k == '-' else tuple(sorted(AB[c] for c in k))
    rows += [r] * int(n)
C.write_inputs(sys.argv[2], rows, 'spec ' + sys.argv[1])
