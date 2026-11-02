import sys, time
sys.path.insert(0, 'work/l41')
from lib import *
fc = F.FastCore(boot_rows=None, ticks=False, fields={'x':0x86}); fc.put('s', open(MST,'rb').read()); fc.load('s'); fc.save('s0')
c = [[('Right',)] * 150 for _ in range(20)]
t = time.time(); rr = fc.run_batch('s0', c, record='last'); print('20x150 noticks', time.time() - t)
fc.close()
