"""python work/l22f/addg.py <stage rows> <n> "<ROW*n;...>" <out>  : rows[:n] + legalized grammar"""
import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
rows=C.rows_of(sys.argv[1])[:int(sys.argv[2])]; w=[]
for sg in sys.argv[3].split(';'):
    r,k=sg.rsplit('*',1); w+=[row(r)]*int(k)
out=list(rows)+legal_after(rows,w)
C.write_inputs(sys.argv[4],out,'addg'); print(len(out))
