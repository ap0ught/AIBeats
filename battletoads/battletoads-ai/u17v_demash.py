"""u17v_demash.py - removes the turbo-like A/B presses of up17 that the game does not need.

    python u17v_demash.py [keepall]

A "mash run" = 4 or more consecutive frames whose inputs are only A / B / nothing and change on every frame
(A,B,A,B,... = each button 30 times a second; or A,-,A,-,...). Inside such a run a press is KEPT only if the game takes
it: the frame polls the controller (not a lag frame in my run1) and the game's own pad byte $29 then shows that
button. Everything else in the run is removed: presses on frames where the controller is not read at all, and presses
on the end-of-level walks where the game reads the port but forces its pad byte to "Right".
The third press of a page lands on the level-load frame, where the game reads it, acts on it and clears $29: a polled
press followed by 4+ unpolled frames with $29 == 0 is kept too.
Runs of fewer than 6 presses that are ordinary play (level byte not a page, pad == input throughout) are left alone.
Output: logs/fix/u17v_demashed_up17.inputs.txt (same header / CRLF format) + logs/fix/u17v_demash_plan.json.
"""
import hashlib
import json
import os
import sys
from pathlib import Path
from u17v_analyze import Cap, FIX

SRC = FIX / "u17v_up17.inputs.txt"
OUT = FIX / "u17v_demashed_up17.inputs.txt"
BITS = {"A": 0x80, "B": 0x40, "Select": 0x20, "Start": 0x10, "Up": 8, "Down": 4, "Left": 2, "Right": 1}

raw = SRC.read_bytes()
lines = raw.decode("ascii").split("\r\n")
assert lines[-1] == ""
head, body = lines[0], lines[1:-1]
ins = [tuple(t for t in ln.split(",") if t) for ln in body]
N = len(ins)
lags = json.loads((FIX / "u17v_run1_lag.json").read_text())
islag = [False] * (N + 2)
prev = 1
for i, l in enumerate(lags, 1):
    islag[i] = l != prev
    prev = l
cap = Cap("run1")
pad = cap.col(0x29)
lv = cap.col(0x10)


def enc(t):
    v = 0
    for b in t:
        v |= BITS[b]
    return v


runs = []
f = 1
while f <= N:
    s = set(ins[f - 1])
    if s and s <= {"A", "B"}:
        g = f
        while g + 1 <= N and set(ins[g]) <= {"A", "B"} and set(ins[g]) != set(ins[g - 1]):
            g += 1
        if g - f + 1 >= 4:
            runs.append((f, g))
        f = g + 1
    else:
        f += 1
plan = []
out = list(ins)
removed = kept = 0
for a, b in runs:
    press = [f for f in range(a, b + 1) if ins[f - 1]]
    play = all(not islag[f] and pad[f - 1] == enc(ins[f - 1]) for f in range(a, b + 1))
    if play and len(press) < 6:
        plan.append({"run": [a, b], "left_alone": "ordinary play, the game reads every frame", "presses": len(press)})
        continue
    keep, drop = [], []
    for f in press:
        taken = (not islag[f]) and pad[f - 1] == enc(ins[f - 1])
        load = (not islag[f]) and pad[f - 1] == 0 and all(islag[g] and pad[g - 1] == 0 for g in range(f + 1, min(N, f + 4) + 1))
        if "keepall" in sys.argv and not islag[f]:
            taken = True
        (keep if (taken or load) else drop).append(f)
    for f in drop:
        out[f - 1] = ()
    removed += len(drop)
    kept += len(keep)
    plan.append({"run": [a, b], "level_bytes": sorted(set(lv[a - 1:b])), "presses": len(press), "removed": len(drop),
                 "kept": [[f, "+".join(ins[f - 1])] for f in keep],
                 "removed_on_polled_frames": sum(1 for f in drop if not islag[f])})
text = head + "\r\n" + "".join(",".join(t) + "\r\n" for t in out)
tmp = str(OUT) + ".tmp"
with open(tmp, "wb") as fh:
    fh.write(text.encode("ascii"))
os.replace(tmp, OUT)
sha = hashlib.sha1(OUT.read_bytes()).hexdigest()
res = {"source": str(SRC), "source_sha1": hashlib.sha1(raw).hexdigest(), "out": str(OUT), "out_sha1": sha,
       "presses_removed": removed, "presses_kept_in_runs": kept, "runs": plan,
       "frames_changed": sum(1 for x, y in zip(ins, out) if x != y)}
(FIX / "u17v_demash_plan.json").write_text(json.dumps(res, indent=1))
print(f"de-mashed list {OUT} sha1 {sha}: {removed} presses removed, {kept} kept in the mash runs, {res['frames_changed']} frames changed")
for p in plan:
    print("  ", p)
