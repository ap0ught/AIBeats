"""print TAS rows a..b with state: python work/l22f/tasrows.py a b"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
a,b=int(sys.argv[1]),int(sys.argv[2])
prev=None
for f in range(a,b+1):
    t=T[f]; inp='+'.join(TR[f-1])
    print(f, f'r{t["room"]} X {ax(t)} y {t["y"]} vy {t["vy"]} coll {t["coll"]} anim {t["anim"]} hp {t["hp"]} np {t["ninpo"]} rng {t["rng"]}', inp)
