"""python work/l32p/amap.py <mst> <rowsfile|-> n  -> collision map after n rows (absolute X)"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C
from ng import fastcore as F
rows = C.rows_of(sys.argv[2]) if sys.argv[2] != '-' else []
n = int(sys.argv[3])
fc=F.FastCore(boot_rows=None); fc.put('s',open(sys.argv[1],'rb').read()); fc.load('s')
if n: fc.step(rows[:n])
r=fc.ram(); fc.close()
s52=r[0x52]-256 if r[0x52]>=128 else r[0x52]; scroll=s52*256+r[0x51]
X,y=scroll+r[0x86],r[0x8A]
print(f'Ryu X {X} y {y} scroll {scroll} bf {r[0xBF]}')
d=C.ROM.read_bytes(); b7=16+7*0x4000
fine = scroll % 16
print('abs X:     '+' '.join(f'{scroll - fine + sx*16:4d}' for sx in range(17)))
for band in range(12):
    yy=64+16*band; line=''
    for sx in range(16):
        t=(d[b7+0xE7CC-0xC000+sx]+r[0x5F])%0xC0
        b=r[0x300+(t+band//2)%0xC0]; k=(b>>4) if band%2==0 else (b&15)
        ch='.' if k==0 else ('ABCDEFGHIJKLMNOP'[k-1] if k>9 else str(k))
        line+='    '+ch
    print(f'{yy:3d}       {line}')
