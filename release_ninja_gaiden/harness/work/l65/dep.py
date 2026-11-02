"""What the fight depends on: r2d5 (and the TAS rows) with pokes of $3E, $62, $381, $394 at control-1, for several bf."""
import sys
sys.path.insert(0, 'work/l65')
from lib65 import *
fc = core65()
r2 = rows_of('work/l63p/dm_r2d5_kill.txt') + [()] * 60
bfs = [243, 74, 102, 123, 0, 111, 37, 190]
base = test_bfs(fc, r2, bfs)
print('base', base, flush=True)
for addr, vals in [(0x3E, [0, 1, 2, 3, 5]), (0x62, [0, 10, 30, 50, 60]), (0x381, [0, 48, 128, 200]), (0x394, [0, 5, 10, 14]), (0x63, [100, 149])]:
    for x in vals:
        o = test_bfs(fc, r2, bfs, pre=[(addr, x)])
        diff = {v: o[v] for v in bfs if o[v][:2] != base[v][:2]}
        print(hex(addr), x, 'same' if not diff else diff, flush=True)
fc.close()
