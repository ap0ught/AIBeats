"""TOWER1: replay a tower segment from its bookmark, dump the 2 KB of RAM every frame and save bookmarks.
    python tw1_probe.py <segment> <tag> [every] [upto]  -> logs/fix/tw1_<tag>.ram, bookmarks tw1_<tag>_f<k> every <every> frames"""
import json, sys, time
from toads.emulator import BizHawk, LOGS_DIR
seg, tag = sys.argv[1], sys.argv[2]; every = int(sys.argv[3]) if len(sys.argv) > 3 else 250
upto = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
ins = [x.replace(",", "+") for x in d["inputs"]][:upto]
e = BizHawk(log_name=f"tw1_probe_{tag}.log")
e.load(d["bookmark"])
buf = bytearray(); t0 = time.time()
for i, b in enumerate(ins):
    if i % every == 0:
        e.save(f"tw1_{tag}_f{i}")
    buf += e.ram(0, 0x800)
    e.step(tuple(v for v in b.split("+") if v), 1)
buf += e.ram(0, 0x800)
open(LOGS_DIR / "fix" / f"tw1_{tag}.ram", "wb").write(buf)
m = e.ram(0, 0x800)
print("frames", len(ins) + 1, "level", m[0x10], "hp", m[0x51A], "lives", m[0x11], "score", bytes(m[0x5F4:0x5FA]).hex(), "secs", round(time.time() - t0, 1), flush=True)
e.close()
