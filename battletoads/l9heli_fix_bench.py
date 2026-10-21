import time
from l9heli_fix_lib import *
e = BizHawk(log_name="l9heli_fix_bench.log"); e.load("L9heli_7819"); e.step((), 1); s = e.msave()
t = time.time()
for i in range(500): e.mload(s); e.step(("Right",), 1); m = e.ram(0, 0x800)
print("mload+step1+ram:", (time.time() - t) / 500 * 1000, "ms")
t = time.time()
for i in range(500): e.mload(s); e.step(("Right",), 2); m = e.ram(0, 0x800); s2 = e.msave(); e.mfree(s2)
print("mload+step2+ram+msave+mfree:", (time.time() - t) / 500 * 1000, "ms")
t = time.time(); e.step(("Right",), 1000); print("1000 plain steps:", (time.time() - t), "s")
e.close()
