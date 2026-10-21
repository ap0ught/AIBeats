"""Why is our toad stuck in the slow walk (cap 96, +2/frame, no sprint) on the floor while the old route sprints at 8308?
Diff the whole RAM of our b1 path at x ~ 743 (frame 248 + 11 Left) against the old run's rows 8300..8307 (toad column and zero page)."""
import json
from l9heli_fix_lib import *
R = cap()
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t4.log"); e.load(g["root"])
for b in g["inputs"][:248] + ["Left"] * 11: e.step(bt(b), 1)
m = e.ram(0, 0x800); print("ours", tstr(m))
for j in (8279, 8303, 8307, 8270):
    ref = bytes(R[OFF + j - 1]); print("old", j, tstr(ref))
    col = [(hex(a), m[a], ref[a]) for a in range(0x3A3, 0x5EC, 15) if m[a] != ref[a]]
    print("   toad column diffs (addr ours old):", col)
    zp = [(hex(a), m[a], ref[a]) for a in range(0x00, 0x100) if m[a] != ref[a]]
    print("   zero page diffs:", zp)
    hi = [(hex(a), m[a], ref[a]) for a in list(range(0x300, 0x3A3)) + list(range(0x5EC, 0x700)) if m[a] != ref[a]]
    print("   $300-3A2/$5EC-6FF diffs:", hi[:60])
e.close()
