"""Track K2: full RAM per frame of a segment prefix -> logs/fix/u17k_ram_<seg>.bin (2048 bytes per frame)."""
import sys
from u17k_lib import *
name, to = sys.argv[1], int(sys.argv[2])
ins = seg(name)[:to]
e = BizHawk(log_name=f"u17k_ramdump_{name}.log")
e.load("B4_end0")
with open(FIX / f"u17k_ram_{name}.bin", "wb") as f:
    for b in ins:
        e.step(bt(b), 1)
        f.write(e.ram(0, 0x800))
e.close()
print("done")
