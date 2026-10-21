"""Can a propeller bug (0x74, hp 15) be hurt or destroyed?  From L9c 7819 (upper step, sprint primed) and from the ledge:
 - run in and press B at various x (running attack), - standing punches at x = 798..816, - jump then B at air frame j, facing right.
Report bug hp / presence (slots 4 and 6) and whether the toad was grabbed."""
from l9heli_fix_lib import *
e = BizHawk(log_name="l9heli_fix_t18.log"); e.load("L9heli_7819"); root = e.msave()
def bugs(m): return [(q, m[0x51A + q]) for q in (4, 6) if m[0x3C1 + q] == 0x74]
def run(seq, tag):
    e.mload(root); grab = None; changed = None
    for i, b in enumerate(seq):
        e.step(bt(b), 1); m = e.ram(0, 0x800); s = toad(m)
        if grab is None and s["an"] in CARRIED: grab = (i + 1, s["x"], s["H"])
        bb = bugs(m)
        if changed is None and bb != [(4, 15), (6, 15)]: changed = (i + 1, bb, s["x"], s["H"], s["an"])
        if s["hp"] < 47: break
    if changed: print("CHANGED", tag, changed, "grab", grab, flush=True)
    return changed, grab
n = 0
# running attack: Right x k then Right+B once, then Right
for k in range(8, 26):
    for hold in (1, 4):
        c, g = run(["Right"] * k + ["Right+B"] * hold + ["Right"] * 30, f"run {k} B{hold}"); n += 1
# walk to the ledge, stop at various x, punch facing right
for k in range(17, 24):
    for stop in (2, 6, 10):
        for nb in (1, 3):
            c, g = run(["Right"] * k + ["Left"] * stop + [""] * 6 + (["Right+B"] + [""] * 14) * nb + [""] * 20, f"punch k{k} stop{stop} x{nb}"); n += 1
# jump from the step / ledge and kick in the air
for k in range(0, 22, 2):
    for a in (2, 4, 8):
        for j in (3, 6, 9, 12, 16):
            c, g = run(["Right"] * k + ["Right+A"] * a + ["Right"] * max(0, j - a) + ["Right+B"] + ["Right"] * 30, f"jump k{k} a{a} B@{j}"); n += 1
print(n, "variants tried")
e.close()
