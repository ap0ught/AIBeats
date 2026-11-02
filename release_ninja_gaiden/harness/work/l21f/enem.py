"""python work/l21f/enem.py <stage rows> n1 n2 [step]: enemies after stage rows[:n] for n in range"""
import sys
sys.path.insert(0,'work/l21f'); sys.path.insert(0,'.')
from lib import *
from ng.solve import hitbox as H
rows=C.rows_of(sys.argv[1]); a,b=int(sys.argv[2]),int(sys.argv[3]); st=int(sys.argv[4]) if len(sys.argv)>4 else 1
fc=core(); fc.step(rows[:a],record='last')
for n in range(a,b+1,st):
    r=fc.ram()
    print(n, 'f', F0+n, 'ryu', r[0x86], r[0x8A], 'BF', r[0xBF], 'hp', r[0x65], [ (e if isinstance(e,dict) else e) for e in H.enemies(r)])
    fc.step(rows[n:n+st],record='last')
fc.close()
