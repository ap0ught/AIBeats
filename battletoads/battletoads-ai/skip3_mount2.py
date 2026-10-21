"""Mount from different depths (y) and see whether the bike drifts to the back lane; then roll back and dive."""
from toads.emulator import BizHawk
def wx(r, s=0): return r[0x3FD + s] | r[0x3EE + s] << 8

def trial(e, approach, pattern, dive_x=1622, n=200, verbose=False):
    e.load("L3_bikes_seen")
    k = 0; mount = None; res = {}
    for j in range(n):
        r = e.ram_all(); x = wx(r)
        if mount is None and r[0x3B5] == 58: mount = k; res["mount"] = (k, x, r[0x41B])
        if (r[0xB7] | r[0xB8] << 8) < 0x800: res["ptr"] = (k, r[0xB7], r[0xB8]); break
        if r[0x439] < 40 and "fell" not in res: res["fell"] = (k, x, r[0x41B])
        if mount is None: b = approach[min(j, len(approach) - 1)]
        elif k - mount < len(pattern): b = pattern[k - mount]
        else: b = "Left+Down" if x <= dive_x else "Left"
        if verbose and j % 3 == 0:
            print(k, b, "x", x, "y", r[0x41B], "h", r[0x439], "st", r[0x3B5], "D5", r[0xD5], "E5", r[0xE5], r[0xE6], flush=True)
        e.step(tuple(v for v in b.split("+") if v), 1); k += 1
    r = e.ram_all(); res["E5"] = (r[0xE5], r[0xE6]); res["lives"] = r[0x11]
    return res

if __name__ == "__main__":
    e = BizHawk(log_name="skip3_mount2.log")
    tas = ["Left+Up", ""] * 4 + ["Left"] * 6
    for name, appr in (("R", ["Right"]), ("RU2", ["Right+Up"] * 2 + ["Right"]), ("RU4", ["Right+Up"] * 4 + ["Right"]),
                       ("RU8", ["Right+Up"] * 8 + ["Right"]), ("RU", ["Right+Up"])):
        print(name, trial(e, appr, tas), flush=True)
    e.close()
