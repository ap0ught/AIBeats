"""compare two RAM dumps with a frame offset: python work/l41/cmp.py <A.bin> <B.bin> [offB-A]
prints first frames where Ryu X/y/hp/room differ (A frame, B frame)."""
import sys
def load(p):
    d = open(p, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
    return f0, [d[i*2048:(i+1)*2048] for i in range(len(d)//2048)]
fa, A = load(sys.argv[1]); fb, B = load(sys.argv[2])
off = int(sys.argv[3]) if len(sys.argv) > 3 else fa - fb
n = 0
for i in range(min(len(A), len(B))):
    a, b = A[i], B[i]
    ka = (a[0x6E], a[0x52]*256+a[0x51]+a[0x86], a[0x8A], a[0x65], a[0x64], a[0xC9])
    kb = (b[0x6E], b[0x52]*256+b[0x51]+b[0x86], b[0x8A], b[0x65], b[0x64], b[0xC9])
    if ka != kb:
        print('A', fa+i+1, ka, 'B', fb+i+1, kb, 'pad', a[0x2A] if len(a)>0x2A else '', b[0x2A]); n += 1
        if n > 15: break
print('lenA', len(A), 'lenB', len(B))
