"""Track C probe: per-frame table of a Level 8 climb (inputs from the placement, bookmark early_L8_p0).
    python u17c_trace.py <climb json> <tag>   -> logs/fix/u17c_trace_<tag>.tsv
columns: frame (since the placement), input, x, height above the placement, z, anim, hp, $0B, $0C, camera y, objects (id:x:H:state byte $3D0)"""
import json
import sys

from u17c_lib import *

j = json.load(open(sys.argv[1]))
tag = sys.argv[2]
e = BizHawk(log_name=f"u17c_trace_{tag}.log")
e.load("early_L8_p0")
m = e.ram(0, 0x800)
base = m[0x439] | m[0x42A] << 8
out = open(FIX / f"u17c_trace_{tag}.tsv", "w", encoding="utf-8")
for i, b in enumerate(j["inputs"], 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    H = (m[0x439] | m[0x42A] << 8) - base
    objs = []
    for q in range(1, 15):
        if m[0x3C1 + q]:
            objs.append(f"{m[0x3C1 + q]:02x}:{m[0x3FD + q] | m[0x3EE + q] << 8}:{(m[0x439 + q] | m[0x42A + q] << 8) - base}:{m[0x3D0 + q]}")
    out.write(f"{i}\t{b}\t{m[0x3FD] | m[0x3EE] << 8}\t{H}\t{m[0x475]}\t{m[0x3B5]}\t{m[0x51A]}\t{m[0x0B]}\t{m[0x0C]}\t{m[0x89] | m[0x8A] << 8}\t{' '.join(objs)}\n")
out.close()
e.close()
print("done", len(j["inputs"]))
