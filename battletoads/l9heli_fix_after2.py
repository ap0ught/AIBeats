"""After the join, with edits: replay the old inputs (L9c 8280..) from a T' bookmark, applying edits, and compare the toad's track with the
old run.  Edits: 'r<idx>=<input>' replace old input idx; 'i<idx>=<n>' insert n idle frames before old input idx; 'd<idx>' drop old input idx.
Alignment: after an insert/drop the comparison index follows the old input being consumed.  Prints the first hp loss / track difference."""
import sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
bm = sys.argv[1]; rep = {}; insert = {}; drop = set()
for a in sys.argv[2:]:
    if a[0] == "r": k, v = a[1:].split("="); rep[int(k)] = v
    elif a[0] == "i": k, v = a[1:].split("="); insert[int(k)] = int(v)
    elif a[0] == "d": drop.add(int(a[1:]))
e = BizHawk(log_name="l9heli_fix_after2.log"); e.load(bm)
first = None; hpd = None; nd = 0; raw = 0
def cmp(k, m):
    global first, hpd, nd
    ref = bytes(R[OFF + k - 1])
    a = (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10]); c = (ref[0x3FD] | ref[0x3EE] << 8, ref[0x439] | ref[0x42A] << 8, ref[0x475], ref[0x51A], ref[0x10])
    if a != c:
        nd += 1
        if first is None: first = (k, a, c); print("first track diff at old index", k, a, c, "| ours", ostr(m), "| old", ostr(ref), flush=True)
        if hpd is None and a[3:] != c[3:]: hpd = (k, a, c); print("first hp/level diff", hpd, "| ours", ostr(m), "| old", ostr(ref), flush=True)
for k in range(8280, 9988):
    for _ in range(insert.get(k, 0)):
        e.step((), 1); raw += 1
    if k in drop: continue
    b = rep.get(k, ins[OFF + k - 1]); e.step(bt(b), 1); raw += 1; m = e.ram(0, 0x800); cmp(k, m)
print("raw frames", raw, "diff frames", nd, "first", first, "hp/level", hpd, "end level", m[0x10], tstr(m), flush=True)
e.close()
