"""Level-entry phase scan (2026-10-10).  After a re-fit the next level's entry RAM equals the old run's, but its random numbers still part
company a few frames later when the CPU time left in the first frames differs (a hidden phase).  This tries one extra Select on each frame
of the tail of a re-fitted segment and looks for a variant after which the next level's first NA frames are bit-identical to the old run
(whole RAM, stack excluded) - then everything behind it replays unchanged.
    python l9heli_fix_entry2.py <entry bookmark> <segment> <S> <E> <old up14 frame of the next level's first input> [NA] [buttons]
Prints every variant with its (segment length, equal frames); the best are listed at the end."""
import json, sys
from l9heli_fix_lib import *
BM, SEG, S, E, F0 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
NA = int(sys.argv[6]) if len(sys.argv) > 6 else 120
BTN = sys.argv[7].split(",") if len(sys.argv) > 7 else ["Select"]
R = cap(); old = up14_inputs()
seg = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json"))["inputs"]; n = len(seg)
e = BizHawk(log_name="l9heli_fix_entry2.log"); e.load(BM)
for b in seg[:S - 1]: e.step(bt(b), 1)
base = e.msave(); VOL = set(range(0x100, 0x200)); ENTRY = bytes(R[F0 - 2])
def eq(m, ref): return not any(m[a] != ref[a] for a in range(0x800) if a not in VOL)
def run(k, btn):
    e.mload(base); m = None
    for i in range(S - 1, n - 6):
        b = seg[i]
        if i + 1 == k: b = (b + "+" + btn).lstrip("+")
        e.step(bt(b), 1)
    for d in range(0, 14):
        m = e.ram(0, 0x800)
        if eq(m, ENTRY):
            same = 0
            for j in range(NA):
                e.step(bt(old[F0 - 1 + j]), 1); mm = e.ram(0, 0x800)
                if eq(mm, bytes(R[F0 - 1 + j])): same += 1
            return n - 6 + d, same
        i = n - 6 + d
        b = seg[i] if i < n else ("A" if (i >= 2 and (seg[i - 2] if i - 2 < n else "") == "A") else "")
        if i + 1 == k: b = (b + "+" + btn).lstrip("+")
        e.step(bt(b), 1)
    return None, 0
r0 = run(-1, ""); print("as fitted: (segment length at which the entry RAM equals the old run's, equal frames of the next", NA, ") =", r0, flush=True)
res = []
for k in range(S, E + 1):
    for b in BTN:
        r = run(k, b); res.append((r[1], r[0], k, b))
        if r[0] is not None and r[1] != r0[1]: print(" ", b, "on", k, "-> segment", r[0], "frames, equal", r[1], flush=True)
res.sort(key=lambda t: (-t[0], t[1] or 10**9))
print("best:", res[:8], "| entries reached:", sum(1 for t in res if t[1] is not None), "of", len(res), flush=True)
e.close()
