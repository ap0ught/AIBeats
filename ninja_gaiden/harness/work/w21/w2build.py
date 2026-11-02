import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21'); sys.path.insert(0,'ng/stages')
from wlib import *
import a56_common as A
TR=A.tas_rows()
P3=C.rows_of('work/w21/p3c2_best.txt')
H=C.rows_of('work/l21f/h_f2_972.inputs.txt')
j,d,k0=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
w=list(P3); w[j:j+2]=[('B','Up'),('B','Right','Up')]
w=w+[('Right',)]*d+[tuple(r) for r in TR[k0:k0+760]]
lg=legal(w,H)
fc=F.FastCore(boot_rows=None); fc.put('s',open('states/mesen/w21_f2_4280.mst','rb').read()); fc.load('s')
_,st,_=fc.step(lg,record='all')
hit=next(i for i,s in enumerate(st) if i>300 and s['room']==3 and C.abs_x(s)>=1177 and s['y']>=97)
print('hit',hit,C.abs_x(st[hit]),st[hit]['y'],st[hit]['ninpo'])
fc.load('s'); fc.step(lg[:hit+1]); fc.save('o'); fc.save_file('o','states/mesen/w21_w2_r3x.mst'); fc.close()
C.write_inputs('work/w21/w2_p3r3.txt',lg[:hit+1],f'w2 pillar spin j{j} d{d} + TAS {k0}..')
C.write_inputs('work/w21/h_w2_r3x.txt',H+lg[:hit+1],'hist')
