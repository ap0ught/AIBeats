import sys,pickle,csv,subprocess; sys.path.insert(0,'.')
from ng.solve import common as C
out=pickle.load(open('work/l12/g4.pkl','rb'))
H=C.rows_of('logs/l11_rep_r1_poweron.inputs.txt')
want=[eval(a) for a in sys.argv[1:]]
for k,m,c in out:
    if m not in want: continue
    c=list(c); st=c[4:][:92]
    rows=H[:2470]+c[:4]+st+[()]*(679-len(st))+[('Start',),('Start',)]+[()]*(834-681)
    tag='l12_try_'+'_'.join(str(x) for x in m).replace("'","")
    C.write_inputs(C.LOGS/f'{tag}.inputs.txt',rows,f'try {m}')
    subprocess.run([sys.executable,'-u','tools/trace_run.py',f'logs/{tag}.inputs.txt',tag],capture_output=True)
    R=list(csv.DictReader(open(f'logs/{tag}.trace.csv')))
    kill=next((int(s['frame'])-2474 for s in R[2474:] if s['bosshp']=='0'),None)
    ctl=next((int(s['frame']) for s in R[2600:] if s['stage']=='2' and s['gm']=='1'),None)
    print(m,'kill',kill,'2-1 ctl',ctl,flush=True)
