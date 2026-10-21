"""Checkpoint-5 snowman (x 244): find a jump whose kick (B in the air, anim 35) reaches the snowman's height
(h 158-164) about 24-32 px in front of it, like TAS #5093 (x 272, h 160). From the follow line's frame 226."""
import json, itertools
from toads.emulator import BizHawk

live = json.load(open("knowledge/l4s_L4n_ledge5_live.json"))
e = BizHawk(log_name="l4kick.log")
e.load("L4n_ledge5"); e.step((), 2)
for b in live[:226]: e.step(tuple(v for v in b.split("+") if v), 1)
root = e.msave()
def snow(m): return [s for s in range(2, 15) if m[0x3C1 + s] == 0x33 and (m[0x3FD + s] | m[0x3EE + s] << 8) == 244]
hits = []
for s, pre, ah, air, bat in itertools.product(range(0, 24, 2), ("", "Left"), (2, 4, 6, 8, 12), ("Left", ""), (2, 6, 10, 14)):
    e.mload(root)
    seq = [pre] * s + ["Left+A"] * ah
    for b in seq: e.step(tuple(v for v in b.split("+") if v), 1)
    k = len(seq); seen = False; got = None
    for j in range(60):
        b = (air, "B") if j >= bat and j < bat + 12 else ((air,) if air else ())
        e.step(tuple(x for x in b if x), 1); k += 1
        m = e.ram(0, 0x800); tx = m[0x3FD] | m[0x3EE] << 8
        sl = snow(m)
        if sl and m[0x51A + sl[0]] > 0: seen = True
        if seen and abs(tx - 244) < 80 and (not sl or m[0x51A + sl[0]] == 0):
            got = k; break
        if m[0x475] == 0 and j > bat + 2: break
    if got: hits.append((got, s, pre, ah, air, bat))
hits.sort()
print("kills:", len(hits), hits[:10])
json.dump(hits[:10], open("knowledge/l4_cp5_kicks.json", "w"))
e.close()
