"""Level 3: replace TAS #5093's banned running jump (Left+Right+A at 13920) with a legal dash-jump, then let the TAS's
own inputs continue (shifted by the frames the dash costs). Score: toad x 180 frames later, rats seen/alive."""
import itertools
from toads.emulator import BizHawk
from l4tas import conv
import l3tas

def main():
    rows = l3tas.load("tas/ram_l3all_1p.txt")
    e = BizHawk(log_name="l3dash.log")
    e.load("L3_tas_13919")
    root = e.msave()
    res = []
    prefixes = []
    for gap in (1, 2):
        for hold in (0, 1, 2, 3):
            for up in (0, 4, 8):
                p = ["Right"] + [""] * gap + ["Right"] * hold + ["Right+A"]
                prefixes.append((gap, hold, up, p))
    for gap, hold, up, p in prefixes:
        for shift in (-1, 0, 1, 2, 3):
            e.mload(root)
            for b in p: e.step(tuple(v for v in b.split("+") if v), 1)
            n = len(p)
            ups = up
            rats = set(); alive_max = 0
            for j in range(1, 200):
                f = 13920 + j - shift
                b = conv(rows[f][0])
                if l3tas.banned(rows[f][0]): b = tuple(x for x in b if x not in ("Left",))
                if ups > 0: b = tuple(set(b) | {"Up"}) if "Down" not in b else b; ups -= 1
                e.step(b, 1)
                m = e.ram(0, 0x800)
                alive = [s for s in range(2, 15) if m[0x3C1 + s] == 0x47 and m[0x51A + s] > 0]
                alive_max = max(alive_max, len(alive))
            m = e.ram(0, 0x800)
            x = m[0x3FD] | m[0x3EE] << 8
            res.append((x, -alive_max, gap, hold, up, shift, m[0x51A]))
    res.sort(reverse=True)
    t = rows[13920 + 199][1]
    print("TAS x at +199:", t[0x3FD] | t[0x3EE] << 8)
    for r in res[:12]: print(r)
    e.close()

if __name__ == "__main__":
    main()
