import sys; sys.path.insert(0,'.')
from ng.inputs import read_inputs, to_mask
rows=read_inputs('logs/tas4751.inputs.txt')
e.load('ref4751/00_1-1_control')   # frame 174
f=e.state().frame
e.trace(True)
s, sent, carry = e.run_comp(rows[f:f+400])
diff=[(f+1+i, '+'.join(a), '+'.join(b)) for i,(a,b) in enumerate(zip(rows[f:f+400], sent)) if tuple(a)!=tuple(b)]
print('rows changed by run_comp:', diff[:10], 'carry', carry)
