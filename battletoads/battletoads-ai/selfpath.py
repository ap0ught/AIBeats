"""Write a follow-mode path log (the TAS watch-log format l4s.py reads) from one of OUR old segments, so a level can
be re-fitted on new RNG by following our own previous line.

    python selfpath.py SEGMENT OUTLOG      e.g. python selfpath.py L8a tas/self_L8a.txt
"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR

def main(seg, out):
    j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    e = BizHawk(log_name="selfpath.log")
    e.load(j["bookmark"])
    with open(out, "w") as f:
        for k, b in enumerate(j["inputs"]):
            e.step(tuple(v for v in b.split("+") if v), 1)
            m = e.ram(0, 0x800)
            x = m[0x3FD] | m[0x3EE] << 8
            f.write(f"f{k} x={x} h={m[0x439]} z={m[0x475]} st={m[0x4B1]} an={m[0x3B5]} hp={m[0x51A]} "
                    f"cam={m[0x87] | m[0x88] << 8} camy={m[0x89] | m[0x8A] << 8} lvl={m[0x10]} in={b or '-'}\n")
    e.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
