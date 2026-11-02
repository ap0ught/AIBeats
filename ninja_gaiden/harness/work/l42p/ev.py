"""events of a 4-2 RAM dump: python work/l42p/ev.py <bin> [rowsfile offset]"""
import sys
d = open(sys.argv[1], 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
n = len(d)//2048
rows = None
if len(sys.argv) > 2:
    sys.path.insert(0, '.')
    from ng.solve import common as C
    rows = C.rows_of(sys.argv[2]); off = int(sys.argv[3])
prev = None; prevt = [0]*8
types = {}
for i in range(n):
    m = d[i*2048:(i+1)*2048]; f = f0 + 1 + i
    scr = m[0x52]*256 + m[0x51]; X = scr + m[0x86]
    s = dict(X=X, y=m[0x8A], hp=m[0x65], np=m[0x64], it=m[0xC9], st=m[0x6D], rm=m[0x6E], BF=m[0xBF], gm=m[0x6C] if False else None)
    out = []
    if prev:
        for k in ('hp', 'np', 'it', 'st', 'rm'):
            if s[k] != prev[k]: out.append(f"{k} {prev[k]}->{s[k]}")
    for j in range(8):
        t = m[0x400+j] if m[0x73] >> j & 1 else 0
        if t and t != prevt[j]:
            out.append(f"spawn s{j} t{t} @{scr+m[0x460+j]},{m[0x480+j]}"); types.setdefault(t, f)
        if not t and prevt[j]: out.append(f"gone s{j} t{prevt[j]}")
        prevt[j] = t
    if out or i % 100 == 0:
        print(f, 'X', X, 'y', s['y'], 'BF', s['BF'], '|', '; '.join(out))
    prev = s
print('types first seen', types)
