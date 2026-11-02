"""Frames where NesHawk's effective pad ($2A) differs from the rows file (input conflicts).
python work/l41p/conflicts.py <rows file> <dump.bin> [...more dumps]"""
import sys
sys.path.insert(0, '.')
from ng import fastcore as F
from ng.solve import common as C
rows = C.rows_of(sys.argv[1])
for p in sys.argv[2:]:
    d = open(p, 'rb').read()[4:]
    B = [d[i*2048:(i+1)*2048] for i in range(len(d)//2048)]
    conf = [14570 + i for i, m in enumerate(B[:1550]) if m[0x2A] != F.to_mask(rows[i])]
    print(p, 'conflict frames (pad != row):', conf[:20])
