"""Can the Level 10 entry be made bit-identical to the old run's, random numbers included?  (2026-10-10)
The dice are zeroed while the level loads and are then driven by the CPU time left over in each frame, so they depend on where inside
a frame the load finished - a hidden phase.  This scans one extra button press (Select by default) on every frame of the last stretch of
Level 9 of a finished line and compares the first frames of Level 10 (whole RAM, stack excluded) with the old run.
    python l9heli_fix_entry.py <tag> <root index> <S: first old index to try> <E: last> [buttons Select,Start,..] [n after]"""
import json, sys, collections
from l9heli_fix_lib import *
TAG, root, S, E = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
BTN = sys.argv[5].split(",") if len(sys.argv) > 5 else ["Select"]
NA = int(sys.argv[6]) if len(sys.argv) > 6 else 30
R = cap(); ins = up14_inputs()
new = json.load(open(LOGS_DIR / f"pbeam_L9heli_{TAG}.json"))["inputs"]
S0 = min(S - 1, 9650) if S <= 9650 else S - 1
assert S0 >= 9650, "only the raw (no-lag) tail is handled"
e = BizHawk(log_name=f"l9heli_fix_entry_{TAG}.log")
goto(e, OFF + root, ins, check=True)
pre = new[root: len(new) - (9987 - S0)]
for b in pre: e.step(bt(b), 1)
base = e.msave(); VOL = set(range(0x100, 0x200))
tail = new[len(new) - (9987 - S0):]                         # the line's inputs for old indices S0+1..9987
def run(extra):
    """extra: {old index: button}; -> (entry RAM equal?, number of the NA following frames whose RAM equals the old run's, signature)"""
    e.mload(base)
    for i, b in enumerate(tail):
        k = S0 + 1 + i
        if k in extra: b = (b + "+" + extra[k]).lstrip("+")
        e.step(bt(b), 1)
    m = e.ram(0, 0x800); ref = bytes(R[OFF + 9987 - 1]); eq0 = not [a for a in range(0x800) if m[a] != ref[a] and a not in VOL]
    same = 0; sig = []
    for j in range(NA):
        F = OFF + 9987 + j
        e.step(bt(ins[F]), 1); m = e.ram(0, 0x800); ref = bytes(R[F])
        if not [a for a in range(0x800) if m[a] != ref[a] and a not in VOL]: same += 1
        if j in (0, 5, 8, 9, 18, 19): sig.append((m[0x1A], m[0x75], m[0x76], bytes(m[0x25:0x29]).hex()))
    return eq0, same, tuple(sig)
r0 = run({}); print("no extra press:", r0, flush=True)
ref = [(int(R[OFF + 9987 + j][0x1A]), int(R[OFF + 9987 + j][0x75]), int(R[OFF + 9987 + j][0x76]), bytes(R[OFF + 9987 + j][0x25:0x29]).hex()) for j in (0, 5, 8, 9, 18, 19)]
print("old run:        ", ref, flush=True)
cls = collections.Counter(); best = []
for k in range(S, E + 1):
    for b in BTN:
        r = run({k: b}); cls[(r[0], r[2])] += 1
        if r[1] == NA: print("IDENTICAL Level 10 start with", b, "at old index", k, flush=True); best.append((k, b))
        elif r[0] and r[1] > 3: print("  ", b, k, "entry equal,", r[1], "of", NA, "following frames equal", flush=True)
print(len(cls), "distinct outcomes over", sum(cls.values()), "candidates; entry-equal:", sum(v for (a, _), v in cls.items() if a), flush=True)
for (a, sg), v in cls.most_common(12): print("  ", v, "x entry equal" if a else "x entry differs", sg[:3], flush=True)
print("identical:", best, flush=True)
e.close()
