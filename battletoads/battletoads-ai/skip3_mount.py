"""Try post-mount input patterns (from L3_bikes_seen, mount inputs up to the mount frame) and report how far back the
bike rolls before the race starts, and whether a dive drops it."""
import json, sys
from toads.emulator import BizHawk

def wx(r, s=0): return r[0x3FD + s] | r[0x3EE + s] << 8

def run(e, pre, pattern, dive_x, dive_btn, n=260, verbose=False):
    e.load("L3_bikes_seen")
    seg = json.load(open("logs/pbeam_L3mount.json"))["inputs"]
    k = 0; mount = None; minx = 9999; fell = None; ram_ptr = None
    for b in seg[:pre]:
        e.step(tuple(x for x in b.split("+") if x), 1); k += 1
    for j in range(n):
        r = e.ram_all()
        if mount is None and r[0x3B5] == 58: mount = k
        x = wx(r); minx = min(minx, x)
        if fell is None and r[0x439] < 50 and r[0x3B5] == 58: fell = (k, x, r[0x41B])
        if (r[0xB7] | r[0xB8] << 8) < 0x800: ram_ptr = (k, r[0xB7], r[0xB8]); break
        if j < len(pattern): b = pattern[j]
        else: b = dive_btn if x <= dive_x else "Left"
        if verbose and j % 3 == 0:
            print(k, b, "cam", r[0x87] | r[0x88] << 8, "x", x, "y", r[0x41B], "h", r[0x439], "st", r[0x3B5], "D5", r[0xD5],
                  "E5", r[0xE5], r[0xE6], "hp", r[0x51A], flush=True)
        e.step(tuple(x for x in b.split("+") if x), 1); k += 1
    r = e.ram_all()
    return dict(mount=mount, minx=minx, fell=fell, ptr=ram_ptr, E5=(r[0xE5], r[0xE6]))

if __name__ == "__main__":
    e = BizHawk(log_name="skip3_mount.log")
    tas = ["Left+Up", ""] * 4 + ["Left"] * 6
    for pre in (13, 15, 17):
        for name, pat in (("tasLU", tas), ("left", ["Left"] * 10), ("leftup", ["Left+Up"] * 10), ("none", [""] * 10)):
            print(pre, name, run(e, pre, pat, 1622, "Left+Down"), flush=True)
    e.close()
