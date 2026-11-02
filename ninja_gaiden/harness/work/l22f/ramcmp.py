import sys
sys.path.insert(0,'work/l22f'); sys.path.insert(0,'.')
from lib import *
fc=FS.boot(list(TR[:6722]), None); tr=fc.ram(); fc.close()
pre=C.rows_of('work/l22f/f0.txt')[:580]
g=legal_after(pre,[('Left',)]*16+[()]*6+[('Right',)]*18)
fc=core(); fc.step(pre+g,record='last'); ou=fc.ram(); fc.close()
print('TAS', tr[0x86], tr[0x8A], 'ours', ou[0x86], ou[0x8A])
for a in range(0x0,0x800):
    if a in range(0x100,0x200): continue
    if tr[a]!=ou[a]: print(hex(a), tr[a], ou[a])
