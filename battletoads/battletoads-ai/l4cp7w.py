"""Level 4, the checkpoint-7 barrier on the new line: l4.cp7_stack's closed loop (crouch under the fast snowballs,
hop the slow ones; the snowmen's own shots break the stack) from bookmark L4r_plats, stopping when the barrier is
down. -> knowledge/l4_cp7_inputs_w.json, bookmark L4r_cp7 (root for the l4warp search).

    python l4cp7.py [punch]     # 'punch': also throw punches at the stack between shots (test)
"""
import inspect
import json
import sys
import textwrap

import l4
from toads.emulator import BizHawk

src = inspect.getsource(l4.cp7_stack)
start = src.index("    hops = 0")
end = src.index("    emu.save(\"L4_cp7_done\")")
body = textwrap.dedent(src[start:end])
emu = BizHawk(log_name="l4cp7.log")
emu.load("L4w_plats")
rec = l4.Rec(emu)


def log(s):
    print(f"[{rec.f}] {s}", flush=True)


for _ in range(120):                                       # the barrier spawns at camera x >= 416
    if l4.find(emu.ram_all(), 0x3c):
        break
    rec.step(("Right",), 1)
exec(body, {**vars(l4), "emu": emu, "rec": rec, "log": log})
r = emu.ram_all()
print("end: frames", rec.f, "toad", l4.toad(r), "wall", l4.find(r, 0x3c), flush=True)
json.dump(rec.inputs, open("knowledge/l4_cp7_inputs_w.json", "w"))
emu.save("L4w_cp7")
emu.close()
