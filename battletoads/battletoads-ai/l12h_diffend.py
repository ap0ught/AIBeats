"""L12h track: diff the RAM of two bookmarks (e.g. two Level-13 entry states).  python l12h_diffend.py <bm1> <bm2> [idle]"""
import sys
from toads.emulator import BizHawk
a, b = sys.argv[1], sys.argv[2]; idle = int(sys.argv[3]) if len(sys.argv) > 3 else 0
e = BizHawk(log_name="fix_l12h_diffend.log")
rams = []
for bm in (a, b):
    e.load(bm); e.step((), 1 + idle); rams.append(e.ram(0, 0x800))
d = [i for i in range(0x800) if rams[0][i] != rams[1][i]]
print(len(d), "differing bytes after", 1 + idle, "idle frames:")
print(" ".join(f"${i:03X}:{rams[0][i]:02X}/{rams[1][i]:02X}" for i in d[:200]))
e.close()
