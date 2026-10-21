"""L12h track: print toad + objects from a RAM dump for a frame range.  python l12h_dump.py <tag> <a> <b> [step]"""
import sys
from toads.emulator import LOGS_DIR
tag, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); st = int(sys.argv[4]) if len(sys.argv) > 4 else 1
buf = open(LOGS_DIR / "fix" / f"{tag}.ram", "rb").read()
for i in range(a, b, st):
    m = buf[i * 2048:(i + 1) * 2048]
    o = " ".join(f"{m[0x3C1+q]:02x}:{m[0x3FD+q] | m[0x3EE+q] << 8},{m[0x439+q] | m[0x42A+q] << 8},{m[0x51A+q]}" for q in range(2, 15) if m[0x3C1 + q])
    print(i, f"x={m[0x3FD] | m[0x3EE] << 8} H={m[0x439] | m[0x42A] << 8} z={m[0x475]} an={m[0x3B5]} spd={m[0x565]} cam={m[0x89] | m[0x8A] << 8} t={m[0x0B]} |", o)
