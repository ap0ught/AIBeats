"""Track K2: full per-frame trace of a Level 6 segment from a bookmark: toad, heads, pauses.
    python u17k_trace.py <segment> <bookmark> [to=2000] -> logs/fix/u17k_trace_<segment>_<bookmark>.txt  (+ .ramsha per frame)"""
import hashlib, json, sys
from u17k_lib import *

name, bm = sys.argv[1], sys.argv[2]
to = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
ins = seg(name)
e = BizHawk(log_name=f"u17k_trace_{name}_{bm}.log")
e.load(bm)
out, sh, prev = [], [], None
for n, b in enumerate(ins[:to], 1):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    t = info(m)
    others = sorted(set(m[0x3C1 + q] for q in range(1, 15) if m[0x3C1 + q] not in (0, 0x4C, 0x4D)))
    p = "PAUSE" if (t["heads"] and prev and t["heads"][0] == prev) else ""
    prev = t["heads"][0] if t["heads"] else None
    out.append(f"{n} {b or '-':8s} toad {t['x']},{t['H']} z{t['z']} a{t['an']} s{t['spd']} f{t['face']} v{t['vy']:.2f} hp{t['hp']} lv{t['lvl']} | heads {t['heads']} {p} | ids {[hex(o) for o in others]} t0B={m[0x0B]} t1A={m[0x1A]}")
    mm = bytearray(m); mm[0x100:0x200] = bytes(256)
    sh.append(hashlib.sha1(bytes(mm)).hexdigest()[:12])
open(FIX / f"u17k_trace_{name}_{bm}.txt", "w").write("\n".join(out) + "\n")
open(FIX / f"u17k_trace_{name}_{bm}.sha", "w").write("\n".join(sh) + "\n")
print(len(out), "rows")
e.close()
