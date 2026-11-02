"""World collision map per room from the TAS 4-3 RAM dump (work/l43p/tas43_ram.bin).
python work/l43/wmap.py <room> [x0 x1]   (rows = y bands 64..255 step 16; '.'=empty 1 rwall 2 lwall 3 both 4-6 corners 7 floor 8 eject 9 ladder)"""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
d = open('work/l43p/tas43_ram.bin', 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
ROM = C.ROM.read_bytes(); b7 = 16 + 7 * 0x4000
room = int(sys.argv[1])
W = {}
for i in range(len(d) // 2048):
    r = d[i*2048:(i+1)*2048]
    if r[0x6E] != room: continue
    s52 = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]
    scr = s52 * 256 + r[0x51]
    if scr % 16: continue
    for sx in range(16):
        t = (ROM[b7 + 0xE7CC - 0xC000 + sx] + r[0x5F]) % 0xC0
        col = []
        for band in range(12):
            b = r[0x300 + (t + band // 2) % 0xC0]
            col.append((b >> 4) if band % 2 == 0 else (b & 15))
        W[(scr + sx * 16) // 16] = col
ks = sorted(W)
x0 = int(sys.argv[2]) // 16 if len(sys.argv) > 2 else ks[0]
x1 = int(sys.argv[3]) // 16 if len(sys.argv) > 3 else ks[-1]
cols = [c for c in range(x0, x1 + 1)]
print('room', room, 'world cols', ks[0]*16, '..', ks[-1]*16)
print('      ' + ''.join(f'{(c*16)//1000 % 10}' for c in cols))
print('      ' + ''.join(f'{(c*16)//100 % 10}' for c in cols))
print('      ' + ''.join(f'{(c*16)//10 % 10}' for c in cols))
for band in range(12):
    line = ''
    for c in cols:
        k = W.get(c, [None]*12)[band]
        line += '?' if k is None else ('.' if k == 0 else ('ABCDEFGHIJKLMNOP'[k-1] if k > 9 else str(k)))
    print(f'{64+16*band:4d}  {line}')
