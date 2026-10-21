"""Replay a full input list from POWER-ON and dump 2 KB RAM + 256 B OAM after every frame (for the video graphics).
    python ramcap.py <inputs.txt> <out>   -> logs/<out>.ram (frames x 2048), logs/<out>.oam (frames x 256),
                                             bookmarks <out>_f<k> every 1000 frames
Row i of each file = the state after input line i+1 has been applied (row 0 = after frame 1)."""
import sys, hashlib
from toads.emulator import BizHawk, LOGS_DIR
src, out = sys.argv[1], sys.argv[2]
lines = [l for l in open(src).read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name=f"ramcap_{out}.log")
ram, oam = open(LOGS_DIR / f"{out}.ram", "wb"), open(LOGS_DIR / f"{out}.oam", "wb")
for i, l in enumerate(lines):
    if i % 1000 == 0:
        e.save(f"{out}_f{i}")
    e.step(tuple(x for x in l.replace(",", "+").split("+") if x), 1)
    ram.write(e.ram(0, 0x800))
    oam.write(e.ram_domain("OAM", 0, 256))
    if i % 5000 == 0:
        print(i, flush=True)
ram.close(); oam.close()
print("frames", len(lines), "ram sha1", hashlib.sha1(e.ram_all()).hexdigest(), flush=True)
e.close()
