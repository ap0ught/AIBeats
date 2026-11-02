"""conflict frames of a NesHawk dump vs its rows: python work/l41/conf.py <bin> <rows>"""
import sys
sys.path.insert(0,'.')
from ng.solve import common as C
BITS = dict(A=0x80, B=0x40, Select=0x20, Start=0x10, Up=0x08, Down=0x04, Left=0x02, Right=0x01)
def mask(r): return sum(BITS[b] for b in r)
d = open(sys.argv[1], 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
rows = C.rows_of(sys.argv[2])
out = []
for i in range(len(d)//2048):
    m = d[i*2048:(i+1)*2048]
    if m[0x2A] != mask(rows[i]): out.append((f0+i+1, m[0x2A], mask(rows[i]), m[0x6E], m[0x65]))
print(len(out)); print(' '.join(str(o[0]) for o in out))
