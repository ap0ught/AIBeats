"""frames behind the TAS by X checkpoint, per room. python work/l41p/lagcmp.py <bin A> [<bin B=TAS>]"""
import sys
def load(p):
    d = open(p, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
    out = []
    for i in range(len(d)//2048):
        m = d[i*2048:(i+1)*2048]
        if m[0x6D] != 8: break
        out.append((f0 + i + 1, m[0x6E], m[0x52]*256 + m[0x51] + m[0x86], m[0x8A], m[0x65]))
    return out
A = load(sys.argv[1]); B = load(sys.argv[2] if len(sys.argv) > 2 else 'work/l41p/tas41_ram.bin')
def first(L, rm, X):
    return next((f for f, r, x, y, h in L if r == rm and x >= X), None)
for rm, xs in ((13, range(100, 2200, 100)), (14, [2171]), (15, range(130, 640, 40))):
    for X in xs:
        a = first(A, rm, X); b = first(B, rm, X)
        print(rm, X, a, b, None if a is None or b is None else a - b)
print('end', A[-1][0] + 1, B[-1][0] + 1)
