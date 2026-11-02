import csv, sys, json
sys.path.insert(0, '.')
from ng.stages import name
rows = list(csv.DictReader(open('logs/tas4751.trace.csv')))
def btn(r): return set(x for x in r['input'].split('+') if x)
# per stage/room segments from 22125
segs = {}
for r in rows:
    f = int(r['frame'])
    if f < 21973: continue
    st, rm = int(r['stage']), int(r['room'])
    b = btn(r)
    k = (name(st), rm)
    d = segs.setdefault(k, dict(first=f, last=f, lr=0, ud=0, udl=0, lr_list=[], ud_list=[], Bpress=0, Apress=0))
    d['last'] = f
    if 'Left' in b and 'Right' in b: d['lr'] += 1; d['lr_list'].append(f)
    if 'Up' in b and 'Down' in b:
        d['ud'] += 1; d['ud_list'].append(f)
        if 'Left' in b or 'Right' in b: d['udl'] += 1
def runs(l):
    out=[]
    for f in l:
        if out and f-out[-1][1]<=3: out[-1][1]=f
        else: out.append([f,f])
    return out
for k,d in segs.items():
    print(k, d['first'], d['last'], 'len', d['last']-d['first']+1, 'LR', d['lr'], 'UD', d['ud'], 'UD+dir', d['udl'])
    print('   LR runs', runs(d['lr_list'])[:30])
    print('   UD runs', runs(d['ud_list'])[:40])
