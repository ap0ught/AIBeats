"""L12h track (2026-10-09): replay a tower segment from its bookmark, dump the 2 KB of RAM every frame and save bookmarks.
    python l12h_probe.py <segment> <tag> [every]   -> logs/fix/<tag>.ram, bookmarks L12h_<tag>_f<k> every <every> frames"""
import json, sys, time
from toads.emulator import BizHawk, LOGS_DIR
seg, tag = sys.argv[1], sys.argv[2]; every = int(sys.argv[3]) if len(sys.argv) > 3 else 250
d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
ins = [x.replace(",", "+") for x in d["inputs"]]
e = BizHawk(log_name=f"fix_l12h_probe_{tag}.log")
e.load(d["bookmark"])
buf = bytearray(); t0 = time.time()
for i, b in enumerate(ins):
    if i % every == 0:
        e.save(f"L12h_{tag}_f{i}")
    buf += e.ram(0, 0x800)
    e.step(tuple(v for v in b.split("+") if v), 1)
buf += e.ram(0, 0x800)
(LOGS_DIR / "fix").mkdir(exist_ok=True)
open(LOGS_DIR / "fix" / f"{tag}.ram", "wb").write(buf)
m = e.ram(0, 0x800)
print("frames", len(ins) + 1, "level", m[0x10], "hp", m[0x51A], "lives", m[0x11], "secs", round(time.time() - t0, 1), flush=True)
e.close()
