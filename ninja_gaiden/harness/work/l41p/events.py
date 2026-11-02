"""events (ninpo/item/hp changes) of a RAM dump: python work/l41p/events.py <bin> <rows file> <row offset: frame f uses rows[f-1-off]>"""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
d = open(sys.argv[1], 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
rows = C.rows_of(sys.argv[2]); off = int(sys.argv[3])
prev = None; prm = None
for i in range(len(d) // 2048):
    m = d[i*2048:(i+1)*2048]; f = f0 + i + 1
    X = m[0x52]*256 + m[0x51] + m[0x86]
    k = (m[0x64], m[0xC9], m[0x65], m[0xC8])
    r = rows[f-1-off] if 0 <= f-1-off < len(rows) else ('?',)
    if prev and k != prev:
        print(f, 'room', m[0x6E], 'X', X, 'y', m[0x8A], 'np', m[0x64], 'item', m[0xC9], 'hp', m[0x65], 'in', '+'.join(r))
    if m[0x6E] != prm: print(f, 'ROOM', m[0x6E], 'X', X, 'y', m[0x8A])
    prev = k; prm = m[0x6E]
    if m[0x6D] != 8: print('end', f); break
