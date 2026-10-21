"""Replay a segment and dump the whole 2 KB of RAM every frame (2026-10-06): what clocks the faces and platforms?
    python l12probe.py <segment> <out>   -> logs/<out>.ram (frames x 2048 bytes), bookmarks <out>_f<k> every 500 frames
"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
seg, out = sys.argv[1], sys.argv[2]
d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
ins = [x.replace(",", "+") for x in d["inputs"]]
e = BizHawk(log_name=f"probe_{out}.log")
e.load(d["bookmark"])
buf = bytearray()
for i, b in enumerate(ins):
    if i % 500 == 0:
        e.save(f"{out}_f{i}")
    buf += e.ram(0, 0x800)
    e.step(tuple(v for v in b.split("+") if v), 1)
buf += e.ram(0, 0x800)
open(LOGS_DIR / f"{out}.ram", "wb").write(buf)
print("frames", len(ins) + 1, "bytes", len(buf), flush=True)
e.close()
