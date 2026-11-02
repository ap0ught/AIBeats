import sys
sys.path.insert(0, '.')
from ng.solve import common as C
d = open(sys.argv[1], 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
rows = C.rows_of('logs/tas4751.inputs.txt')
prev = None
for i in range(len(d) // 2048):
    m = d[i*2048:(i+1)*2048]; f = f0 + i + 1
    X = m[0x52]*256 + m[0x51] + m[0x86]
    k = (m[0x64], m[0xC9], m[0x65], m[0xC8])
    if prev and k != prev:
        print(f, 'X', X, 'y', m[0x8A], 'np', m[0x64], 'item', m[0xC9], 'hp', m[0x65], 'in', '+'.join(rows[f-1]))
    prev = k
    if m[0x6D] != 6: print('end', f); break
