import sys, time
sys.path.insert(0, 'work/l41')
from lib import *
fc = core()
fc.save('s0')
c = [[('Right',)] * 150 for _ in range(100)]
t = time.time(); rr = fc.run_batch('s0', c, record='last'); print('100x150 last', time.time() - t)
t = time.time(); rr = fc.run_batch('s0', c, record='all'); print('100x150 all', time.time() - t)
c1 = [[('Right',)] for _ in range(100)]
t = time.time(); rr = fc.run_batch('s0', c1, record='all', keep=True); print('100x1 keep', time.time() - t)
fc.close()
