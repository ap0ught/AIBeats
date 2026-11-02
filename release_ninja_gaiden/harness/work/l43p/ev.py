"""events of a 4-3 RAM dump: python work/l43p/ev.py <bin> [every]"""
import sys
d = open(sys.argv[1], 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
every = int(sys.argv[2]) if len(sys.argv) > 2 else 0
n = len(d)//2048
prev = None; prevt = [0]*8
def P(p):
    s=''
    for b,c in ((0x80,'A'),(0x40,'B'),(0x10,'S'),(0x08,'U'),(0x04,'D'),(0x02,'L'),(0x01,'R')):
        if p & b: s += c
    return s or '.'
for i in range(n):
    m = d[i*2048:(i+1)*2048]; f = f0 + 1 + i
    scr = m[0x52]*256 + m[0x51]; X = scr + m[0x86]
    s = dict(X=X, y=m[0x8A], hp=m[0x65], np=m[0x64], it=m[0xC9], st=m[0x6D], rm=m[0x6E], BF=m[0xBF], rf=m[0x84])
    out = []
    if prev:
        for k in ('hp', 'np', 'it', 'st', 'rm'):
            if s[k] != prev[k]: out.append(f"{k} {prev[k]}->{s[k]}")
    for j in range(8):
        t = m[0x400+j] if m[0x73] >> j & 1 else 0
        if t and t != prevt[j]:
            out.append(f"spawn s{j} t{t} @{scr+m[0x460+j]},{m[0x480+j]}")
        if not t and prevt[j]: out.append(f"gone s{j} t{prevt[j]}")
        prevt[j] = t
    if out or (every and i % every == 0):
        print(f, 'rm', s['rm'], 'X', X, 'y', s['y'], 'BF', s['BF'], 'pad', P(m[0x2A]), '|', '; '.join(out))
    prev = s
