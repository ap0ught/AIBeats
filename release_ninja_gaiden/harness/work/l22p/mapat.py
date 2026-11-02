"""python work/l22p/mapat.py <mst> ["spec"]  ring collision map (32 cols from scroll-128) + enemies"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21')
from ng.solve import common as C, hitbox as H
from ng import fastcore as F
from wlib import spec
fc=F.FastCore(boot_rows=None); fc.put('s',open(sys.argv[1],'rb').read()); fc.load('s')
if len(sys.argv)>2 and sys.argv[2]: fc.step(spec(sys.argv[2]))
r=fc.ram(); fc.close()
s52=r[0x52]-256 if r[0x52]>=128 else r[0x52]; scroll=s52*256+r[0x51]; X,y=scroll+r[0x86],r[0x8A]
print(f'Ryu X {X} y {y} scroll {scroll} room {r[0x6E]} bf {r[0xBF]}')
c0=scroll//16-8; c1=c0+32
print('     '+''.join(str((c*16//100)%10) for c in range(c0,c1)))
print('     '+''.join(str((c*16//10)%10) for c in range(c0,c1)))
for band in range(12):
    yy=64+16*band; line=''
    for c in range(c0,c1):
        b=r[0x300+6*(c%32)+band//2]; k=(b>>4) if band%2==0 else (b&15)
        ch='.' if k==0 else ('ABCDEFGHIJKLMNOP'[k-1] if k>9 else str(k))
        if c*16<=X<c*16+16 and yy<=y<yy+16: ch='@'
        line+=ch
    print(f'{yy:3d}  {line}')
for e in H.enemies(r): print('   enemy',e['slot'],'type',e['type'],'X',scroll+e['x'],'y',e['y'],'hp',e['hp'])
