"""l62: finish 6-2: rows (from 33590) -> trigger ($5C 2->0 in room 40) -> Right from trigger+1 through the 6-3 control row (trigger+279).
python work/l62/fin.py rows.txt out_stage.txt out_poweron.txt"""
import sys; sys.path.insert(0,'work/l62')
from lib62 import *
r=rows_file(sys.argv[1])
fc=base(mst='states/mesen/l62_33589.mst')
r=r+[row('Right')]*80
st=run(fc,r)
trig=next(33590+i for i,s in enumerate(st) if i>0 and s['room6e']==40 and st[i-1]['e5c']==2 and s['e5c']==0 and RXY(s)[0]>600)
s=st[trig-33590]; print('trigger', trig, RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'item', s['item'])
rows=r[:trig-33589]; rows+=[row('Right')]*(trig+279-33589-len(rows))
st=run(fc,rows+[row('Right')]*3)
ld=next((33590+i for i,x in enumerate(st) if x['st6d']==18),None)
print('6-3 load', ld, 'control row', trig+279, 'BF at control row', st[trig+279-33590]['bf'], '(f-27)%256', (trig+279-27)%256, 'np', st[-1]['np64'], 'item', st[-1]['item'], 'hp', st[-1]['hp65'], 'legal', legal_ok(rows) or 'ok')
wrows(sys.argv[2], rows, f'l62 6-2 stage rows from 33,590 (room 37) to the 6-3 control row {trig+279}; trigger {trig}')
src=open('work/l62/l62_hs_k2_poweron.inputs.txt').read().split('\n')[1:33590]
R=src+[('+'.join(x)) for x in rows]
open(sys.argv[3],'w').write(f'# frames={len(R)}\n'+'\n'.join(R)+'\n'); print('poweron rows', len(R))
fc.close()
