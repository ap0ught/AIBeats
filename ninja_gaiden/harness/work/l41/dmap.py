"""collision map from a RAM dump frame: python work/l41/dmap.py <bin> <frame>"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C, hitbox as H
d=open(sys.argv[1],'rb').read(); f0=int.from_bytes(d[:4],'little'); d=d[4:]
f=int(sys.argv[2]); r=d[(f-f0-1)*2048:(f-f0)*2048]
scroll=r[0x52]*256+r[0x51]; X,y=scroll+r[0x86],r[0x8A]
print(f'frame {f} Ryu X {X} x {r[0x86]} y {y} scroll {scroll} room {r[0x6E]}')
rom=C.ROM.read_bytes(); b7=16+7*0x4000
print('     '+' '.join(f'{sx*16:3d}' for sx in range(16)))
for band in range(12):
    yy=64+16*band; line=''
    for sx in range(16):
        t=(rom[b7+0xE7CC-0xC000+sx]+r[0x5F])%0xC0
        b=r[0x300+(t+band//2)%0xC0]; k=(b>>4) if band%2==0 else (b&15)
        ch='.' if k==0 else ('ABCDEFGHIJKLMNOP'[k-1] if k>9 else str(k))
        if sx*16<=r[0x86]<sx*16+16 and yy<=y<yy+16: ch='@'
        line+='   '+ch
    print(f'{yy:3d}  {line}')
