"""per-frame detail of a RAM dump: python work/l32p/det.py <bin> <from> <to> [rowsfile offset]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
d = open(sys.argv[1], 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
a, b = int(sys.argv[2]), int(sys.argv[3])
rows = None
if len(sys.argv) > 4:
    from ng.solve import common as C
    rows = C.rows_of(sys.argv[4]); off = int(sys.argv[5])
for f in range(a, b + 1):
    i = f - f0 - 1
    m = d[i*2048:(i+1)*2048]
    X = m[0x52]*256 + m[0x51] + m[0x86]
    scr = m[0x52]*256 + m[0x51]
    en = []
    for j in range(8):
        if m[0x73] >> j & 1:
            en.append(f"{j}:t{m[0x400+j]}s{m[0x410+j]}T{m[0x408+j]}@{scr+m[0x460+j]},{m[0x480+j]}")
    inp = ''
    if rows is not None:
        k = f - off
        inp = '+'.join(rows[k-1]) if 0 < k <= len(rows) else '?'
    print(f, inp or '-', 'X', X, 'x', m[0x86], 'y', m[0x8A], 'hp', m[0x65], 'inv', m[0x95], 'np', m[0x64], 'BF', m[0xBF], ' '.join(en))
