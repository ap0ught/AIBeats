"""side by side TAS vs ours (from trace csvs) by stage time t: python work/rep/sbs.py ours.trace.csv t0 t1 [lag]"""
import csv,sys
sys.path.insert(0,'.')
from ng.solve import common as C
T=list(csv.DictReader(open('logs/tas4751.trace.csv')))
O=list(csv.DictReader(open(sys.argv[1])))
a,b=int(sys.argv[2]),int(sys.argv[3]); lag=int(sys.argv[4]) if len(sys.argv)>4 else 0
def d(r): return {k:int(v) for k,v in r.items() if v.lstrip('-').isdigit()}
for t in range(a,b):
    tr=d(T[174+t-1]); 
    s=f"t {t:4d} TAS x {C.abs_x(tr):4d} y {tr['y']:3d} hp {tr['hp']:2d} np {tr['ninpo']:2d} {T[174+t-1]['input']:18s}"
    if 174+t+lag-1 < len(O):
        o=d(O[174+t+lag-1])
        s+=f"| ours t {t+lag:4d} x {C.abs_x(o):4d} y {o['y']:3d} hp {o['hp']:2d} np {o['ninpo']:2d} {O[174+t+lag-1]['input']}"
    print(s)
