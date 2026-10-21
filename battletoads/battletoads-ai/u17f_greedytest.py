import sys
from u17f_lib import *
bm, LVL = sys.argv[1], int(sys.argv[2])
e = BizHawk(log_name="u17f_greedytest.log")
e.load(bm)
def sig():
    m = e.ram(0, 0x800)
    return m[0x10], m[0x51A] == 0, (m[0x3FD] | m[0x3EE] << 8) == 0
head, stage = [], 0
for k in range(80):
    s0 = e.msave()
    e.step((), 1)
    e.step((), 1)
    idle = sig()
    choice = ""
    tried = {}
    for b in ("A", "B"):
        e.mload(s0)
        e.step((b,), 1)
        e.step((), 1)
        tried[b] = sig()
        if tried[b] != idle:
            choice = b
            break
    e.mload(s0)
    e.step((choice,) if choice else (), 1)
    e.mfree(s0)
    head.append(choice)
    m = e.ram(0, 0x800)
    stage = placed_stage(stage, m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, LVL)
    print(k, repr(choice), idle, tried, stage, flush=True)
    if stage == 3:
        break
print(len(head), [(i, b) for i, b in enumerate(head) if b])
e.close()
