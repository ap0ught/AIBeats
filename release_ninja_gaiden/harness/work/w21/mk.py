"""python work/w21/mk.py <power-on rows> <trace csv|-> <out mst>"""
import sys; sys.path.insert(0,'.')
from ng.solve import common as C, fast as FS
H=C.rows_of(sys.argv[1]); print(len(H))
fc=FS.boot(H,None if sys.argv[2]=='-' else sys.argv[2]); r=fc.ram()
print('x',r[0x86],'y',r[0x8A],'bf',r[0xBF],'hp',r[0x65],'np',r[0x64],'stage',r[0x6D],'room',r[0x6E],'anim',r[0x80],'rf',r[0x84])
fc.save('s'); fc.save_file('s',sys.argv[3],frame=len(H)); fc.close()
