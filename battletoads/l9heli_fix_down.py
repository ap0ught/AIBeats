"""Replay a finished Level 9 line (logs/pbeam_L9heli_<tag>.json) from the old run's bookmark and then the old inputs of the later levels,
comparing the WHOLE RAM with the old run frame for frame (old up14 frame F <-> new frame F - gain).
    python l9heli_fix_down.py <tag> <root index> <frames> [drop a,b,..: old up14 frames whose input is left out] [dup a,b,..: frames played twice]"""
import json, sys
from l9heli_fix_lib import *
TAG, root, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
DROP = set(int(v) for v in sys.argv[4].split(",") if v not in ("", "-")) if len(sys.argv) > 4 else set()
DUP = set(int(v) for v in sys.argv[5].split(",") if v not in ("", "-")) if len(sys.argv) > 5 else set()
R = cap(); ins = up14_inputs(); NF = len(ins)
new = json.load(open(LOGS_DIR / f"pbeam_L9heli_{TAG}.json"))["inputs"]
e = BizHawk(log_name=f"l9heli_fix_down_{TAG}.log")
goto(e, OFF + root, ins, check=True)
for b in new[root:]:
    e.step(bt(b), 1)
VOL = set(range(0x100, 0x200))
import os
TRACK = bool(os.environ.get("TRACK")); TRK = (0x10, 0x11, 0x3FD, 0x3EE, 0x439, 0x42A, 0x51A, 0x585)
shift = 0; shown = 0; nd = 0; firsts = []
seq = []
for F in range(OFF + 9987, min(NF, OFF + 9987 + N)):
    if (F + 1) in DROP: shift -= 1; continue
    seq.append((F, ins[F]))
    if (F + 1) in DUP: seq.append((F, ins[F]))
prevF = None
for F, b in seq:
    e.step(bt(b), 1); m = e.ram(0, 0x800); ref = bytes(R[F])
    d = [a for a in (TRK if TRACK else range(0x800)) if m[a] != ref[a] and a not in VOL]
    if d:
        nd += 1
        if shown < 12:
            shown += 1
            print(f"old up14 frame {F + 1}: {len(d)} bytes differ: {[(hex(a), m[a], ref[a]) for a in d[:14]]} | level ours {m[0x10]} old {ref[0x10]} t {m[0x0B]}/{ref[0x0B]}", flush=True)
print(f"{len(seq)} frames, {nd} with differences", flush=True)
print("last frame: level", m[0x10], "x", m[0x3FD] | m[0x3EE] << 8, "hp", m[0x51A], "lives", m[0x11], "| old", ref[0x10], ref[0x3FD] | ref[0x3EE] << 8, ref[0x51A], ref[0x11], flush=True)
e.close()
