"""python work/l22c/tasen.py N0 N1 [every]: TAS state at N0 (boot), step TAS rows, print enemies"""
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'ng/stages')
from ng.solve import common as C, fast as FS, hitbox as H
import a56_common as A
TR=A.tas_rows(); a,b=int(sys.argv[1]),int(sys.argv[2]); ev=int(sys.argv[3]) if len(sys.argv)>3 else 3
fc=FS.boot(TR[:a],'logs/tas4751.trace.csv')
for f in range(a,b):
    m=fc.ram()
    if (f-a)%ev==0:
        s52=m[0x52]-256 if m[0x52]>=128 else m[0x52]; sc=s52*256+m[0x51]
        print(f,'ryu X',sc+m[0x86],'y',m[0x8A],'hp',m[0x65],'sc',sc,'en',[(e['slot'],e['type'],sc+e['x'],e['y']) for e in H.enemies(m)])
    fc.step([TR[f]],record='last')
fc.close()
