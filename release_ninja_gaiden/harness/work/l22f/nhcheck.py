"""NesHawk trace of HIST+stage rows vs Mesen (lib core): conflicts after F0 + first difference.
python work/l22f/nhcheck.py <stage rows> <tag> [--notrace]"""
import csv, subprocess, sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
rows=C.rows_of(sys.argv[1]); tag=sys.argv[2]
full=list(HIST)+list(rows)
pf=f'work/l22f/{tag}_pw.txt'
C.write_inputs(pf, full, 'power-on + 2-2 rows')
if '--notrace' not in sys.argv:
    subprocess.run([sys.executable,'tools/trace_run.py',pf,tag],check=True,stdout=subprocess.DEVNULL)
T=list(csv.DictReader(open(f'logs/{tag}.trace.csv')))
pads=F.neshawk_pads(f'logs/{tag}.trace.csv', len(full)); m=F.masks_of(full)
conf=[i+1 for i,(a,b) in enumerate(zip(pads,m)) if a!=b and i>=F0]
print('NesHawk conflicts after control:', conf)
r=play(rows, stops=[])
first=None
for i,s in enumerate(r.states):
    t={k:int(v) for k,v in T[F0+i].items() if v.lstrip('-').isdigit()}
    if (ax(s),s['y'],s['hp'],s['ninpo'],s['stage'])!=(C.abs_x(t),t['y'],t['hp'],t['ninpo'],t['stage']):
        first=(F0+i+1,ax(s),s['y'],s['hp'],C.abs_x(t),t['y'],t['hp']); break
print('first Mesen/NesHawk difference:', first)
t={k:int(v) for k,v in T[-1].items() if v.lstrip('-').isdigit()}
print('NesHawk end frame',t['frame'],'stage',t['stage'],'room',t['room'],'X',C.abs_x(t),'y',t['y'],'hp',t['hp'],'np',t['ninpo'])
