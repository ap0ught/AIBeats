"""Replay TAS #5093's bike-mount-and-dive inputs from L3_bikes_seen, with the Right run-in length as a parameter."""
import sys
from toads.emulator import BizHawk
def wx(r, s=0): return r[0x3FD + s] | r[0x3EE + s] << 8

def tas_seq(nright, nlu=11, nleft=31, ndown=130):
    s = ["Right"] * nright
    for i in range(nlu): s += ["Left+Up", ""]
    s += ["Left+Up"] + ["Left"] * nleft + ["Left+Down"] * ndown
    return s

def trial(e, seq, verbose=False):
    e.load("L3_bikes_seen")
    res = {}
    for k, b in enumerate(seq):
        r = e.ram_all(); x = wx(r)
        if "mount" not in res and r[0x3B5] == 58: res["mount"] = (k, x, r[0x41B])
        if (r[0xB7] | r[0xB8] << 8) < 0x800: res["ptr"] = (k, r[0xB7], r[0xB8]); break
        if r[0x439] < 40 and "fell" not in res: res["fell"] = (k, x, r[0x41B])
        if verbose and k % 3 == 0:
            print(k, b, "x", x, "y", r[0x41B], "h", r[0x439], "st", r[0x3B5], "D5", r[0xD5], "E5", r[0xE5], r[0xE6], "hp", r[0x51A], flush=True)
        e.step(tuple(v for v in b.split("+") if v), 1)
    r = e.ram_all(); res["E5"] = (r[0xE5], r[0xE6]); res["lives"] = r[0x11]; res["B7"] = (r[0xB7], r[0xB8])
    return res

if __name__ == "__main__":
    e = BizHawk(log_name="skip3_tas.log")
    if len(sys.argv) > 1:
        print(trial(e, tas_seq(int(sys.argv[1])), verbose=True))
    else:
        for nr in range(2, 10):
            print(nr, trial(e, tas_seq(nr)), flush=True)
    e.close()
