"""Skip the L4 intro (mash B), align the toad's placement with TAS #5093's (frame 15311) and replay the TAS's inputs,
comparing against its RAM each frame. Reports how far it stays in sync."""
import sys
from toads.emulator import BizHawk
from l4tas import load_tas, conv, key

def placed(m): return m[0x10] == 4 and m[0x3FD] == 32 and m[0x3EE] == 0 and m[0x41B] == 216

def main(shifts):
    rows = load_tas()
    e = BizHawk(log_name="l4tas2.log")
    e.load("L3skip_end")
    for k in range(400):
        e.step(("B",) if k % 2 == 0 else (), 1)
        if placed(e.ram(0, 0x800)): break
    e.save("L4_skip_placed")
    print("placed after", k + 1, "frames", flush=True)
    for s in shifts:
        e.load("L4_skip_placed")
        bad = None
        for j in range(1, 1500):
            f = 15311 + s + j
            e.step(conv(rows[f][0]), 1)
            m = e.ram(0, 0x800); tm = rows[15311 + j][1]
            if key(m) != key(tm):
                bad = (j, key(m), key(tm)); break
        print("shift", s, "first mismatch", bad, flush=True)
    e.close()

if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [-2, -1, 0, 1, 2])
