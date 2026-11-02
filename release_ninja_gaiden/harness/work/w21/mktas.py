import sys; sys.path.insert(0,'.'); sys.path.insert(0,'ng/stages')
from ng.solve import common as C, fast as FS
import a56_common as A
TR=A.tas_rows()
for N in map(int,sys.argv[1:]):
    fc=FS.boot(TR[:N],'logs/tas4751.trace.csv'); r=fc.ram()
    print(N,'x',r[0x86],'y',r[0x8A],'bf',r[0xBF],'hp',r[0x65],'stage',r[0x6D],'room',r[0x6E])
    fc.save('s'); fc.save_file('s',f'states/mesen/w21_tas{N}.mst',frame=N); fc.close()
