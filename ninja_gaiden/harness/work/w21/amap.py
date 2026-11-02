"""python work/w21/amap.py <mst> "<spec>" t1,t2  -> collision map at those rows (absolute X)"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from ng.solve import common as C, hitbox as H
from ng import fastcore as F
from try_ import spec_rows, legal
rows=legal(spec_rows(sys.argv[2])) if sys.argv[2] else []
fc=F.FastCore(boot_rows=None); fc.put('s',open(sys.argv[1],'rb').read()); fc.load('s')
done=0
for t in [int(v) for v in sys.argv[3].split(',')]:
    if t>done: fc.step(rows[done:t]); done=t
    r=fc.ram()
    s52=r[0x52]-256 if r[0x52]>=128 else r[0x52]; scroll=s52*256+r[0x51]
    X,y=scroll+r[0x86],r[0x8A]
    print(f't {t} Ryu X {X} y {y} scroll {scroll} room {r[0x6E]} bf {r[0xBF]}')
    d=C.ROM.read_bytes(); b7=16+7*0x4000
    print('screen x/10: '+' '.join(f'{sx*16:3d}' for sx in range(16)))
    for band in range(12):
        yy=64+16*band; line=''
        for sx in range(16):
            c=sx
            t=(d[b7+0xE7CC-0xC000+sx]+r[0x5F])%0xC0
            b=r[0x300+(t+band//2)%0xC0]; k=(b>>4) if band%2==0 else (b&15)
            ch='.' if k==0 else ('ABCDEFGHIJKLMNOP'[k-1] if k>9 else str(k))
            if sx*16<=r[0x86]<sx*16+16 and yy<=y<yy+16: ch='@'
            line+='   '+ch
        print(f'{yy:3d}        {line}')
    for e in H.enemies(r):
        print('   enemy',e['slot'],'type',e['type'],'pose',e['pose'],'X',scroll+e['x'],'y',e['y'],'hp',e['hp'])
fc.close()
