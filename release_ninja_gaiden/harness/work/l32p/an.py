"""analyse a RAM dump (tas32.py format): enemy slot events. python work/l32p/an.py <bin> [type filter]"""
import sys
d = open(sys.argv[1], 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
flt = int(sys.argv[2]) if len(sys.argv) > 2 else None
N = len(d) // 2048
prev = {}
for i in range(N):
    m = d[i*2048:(i+1)*2048]; f = f0 + i + 1
    X = m[0x52]*256 + m[0x51] + m[0x86]
    for j in range(8):
        busy = m[0x73] >> j & 1
        t = m[0x400+j] if busy else None
        st = m[0x410+j] if busy else None
        k = (t, st)
        if prev.get(j) != k:
            if flt is None or t == flt or (prev.get(j) or (None,))[0] == flt:
                ex = m[0x460+j] ; ey = m[0x480+j]
                print(f, 'X', X, 'y', m[0x8A], 'hp', m[0x65], 'BF', m[0xBF], 'slot', j, 'type', t, 'state', st, 'timer', m[0x408+j], 'ex', ex, 'ey', ey, 'ehp', m[0x490+j])
            prev[j] = k
    if m[0x6D] != 6: print('stage change', f); break
