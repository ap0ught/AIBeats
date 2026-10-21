"""After the join: replay the old inputs (L9c 8280..9987) from a T' bookmark and compare the toad's track with the old run (cap14).
Prints the first difference, the frames around it (objects too), and the outcome.   python l9heli_fix_after.py <bookmark> [select frames...]
Extra args = old indices at which Select is added (a re-roll, as rngfit does)."""
import sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
bm = sys.argv[1]; sel = set(int(v) for v in sys.argv[2:])
e = BizHawk(log_name="l9heli_fix_after.log"); e.load(bm)
first = None; nd = 0; hpd = None; lag = 0
for k in range(8279, 9987):
    b = ins[OFF + k]
    if (k + 1) in sel: b = (b + ",Select").lstrip(",")
    e.step(bt(b), 1); m = e.ram(0, 0x800); ref = bytes(R[OFF + k])
    a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
    if a != c:
        nd += 1
        if first is None:
            first = k + 1; print("first diff at old index", k + 1, "ours", a, "old", c, "| ours:", tstr(m), "|", ostr(m)); print("   old:", tstr(ref), "|", ostr(ref), flush=True)
        if hpd is None and a[3:] != c[3:]: hpd = (k + 1, a, c); print("first hp/level diff", hpd, "| ours objs:", ostr(m), "| old objs:", ostr(ref), flush=True)
print("diff frames", nd, "first", first, "hp/level", hpd, "| end: ours", tstr(m), "level", m[0x10], "old level", ref[0x10], flush=True)
d = [x for x in range(0x800) if m[x] != ref[x]]
print("end RAM diffs", len(d), [hex(x) for x in d[:40]])
e.close()
