"""Round 4: follow the legalized TAS line, repair each divergence with a short A* to a later TAS standing point, re-align
and follow again. One stage, unattended.
    python work/r4/tasrepair.py <stage> <state> <base rows name|-> <k0> <kend> <tag> [--hist f] [--ahead 25]
           [--w 1.3] [--max-exp 600] [--iters 30]
k0 = TAS frame our base end matches (TAS rows k0.. are appended); kend = last TAS frame to follow (next load).
Outputs logs/r4/<tag>_p<i> (follow), <tag>_a<i> (repair); log lines 'ITER'. The A* goal is the TAS position at the
first frame >= divergence + ahead where the TAS stands on the ground (anim 0/1/3, not airborne) in the same room;
if the TAS changes room first, the goal is that room change (room:<r>:<exit wpos>:<exit y>)."""
import csv
import os
import re
import subprocess
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent.parent
a = sys.argv[1:]


def opt(n, d):
    if n in a:
        i = a.index(n)
        v = a[i + 1]
        del a[i:i + 2]
        return type(d)(v)
    return d


hist = opt("--hist", "")
ahead = opt("--ahead", 25)
w = opt("--w", "1.3")
mx = opt("--max-exp", "600")
iters = opt("--iters", 30)
TOL = opt("--tol", 6)
GTOL = opt("--gtol", 2)
stage, st, base, k0, kend, tag = a[0], a[1], a[2], int(a[3]), int(a[4]), a[5]
T = {int(r["frame"]): r for r in csv.DictReader(open(P / "logs/tas4751.trace.csv"))}


def wp(d):
    sc = int(d["scroll_scr"])
    sc = sc - 256 if sc >= 128 else sc
    return sc * 256 + int(d["scroll"]) + int(d["x"])


def run(cmd, log):
    env = dict(os.environ, A34_AIRRUN="1", A34_HMAX="1", A34_SWITCH="1")
    with open(log, "w") as f:
        subprocess.run(cmd, cwd=str(P), env=env, stdout=f, stderr=subprocess.STDOUT)
    return Path(log).read_text()


for it in range(iters):
    pout = f"{tag}_p{it}"
    cmd = [sys.executable, "-u", "work/r4/tasprefix.py", st, base, str(k0), str(kend), pout, "--tol", str(TOL), "--back", "3"]
    if hist:
        cmd += ["--hist", hist]
    txt = run(cmd, P / "logs" / "r4" / f"{pout}.out")
    m = re.search(r"diverge at TAS frame (\d+)", txt)
    we = re.search(r"wrote \S+ rows (\d+) end frame (\S+) room (\S+)", txt)
    print("ITER", it, "follow", k0, "->", m.group(1) if m else "END", "|", we.group(0) if we else txt[-300:], flush=True)
    if not m:
        print("DONE (no divergence up to", kend, ")", pout, flush=True)
        break
    D = int(m.group(1))
    # target: first TAS frame >= D + ahead standing in the same room, or the room change before it
    room = int(T[D]["room"])
    kT, goal = None, None
    for f in range(D + ahead, kend):
        R = T[f]
        if int(R["room"]) != room:
            P0 = T[f - 1]
            goal = f"room:{R['room']}:{wp(P0)}:{P0['y']}"
            kT = f - 1
            break
        if int(R["anim"]) in (0, 1, 3) and not (int(R["rflags"]) & 4):
            goal = f"pos:{room}:{wp(R)}:{R['y']}:{GTOL}"
            kT = f
            break
    if goal is None:
        print("no target", flush=True)
        break
    aout = f"{tag}_a{it}"
    cmd = [sys.executable, "-u", "work/r4/astar.py", stage, st, pout, goal, aout, "--w", w, "--max-exp", mx]
    txt = run(cmd, P / "logs" / "r4" / f"{aout}.out")
    res = [l for l in txt.splitlines() if l.startswith("RESULT")]
    print("ITER", it, "repair", goal, "TAS frame", kT, "|", res[-1] if res else "NO GOAL", flush=True)
    if not res:
        break
    gm = re.search(r"goal at (\d+)", res[-1])
    base = aout
    if goal.startswith("room:"):
        # we are in the new room at its first frame: align to the TAS's room-change frame
        k0 = kT + 1
    else:
        k0 = kT
    print("ITER", it, "our frame", gm.group(1) if gm else "?", "aligned to TAS", k0, "lag", (int(gm.group(1)) - k0) if gm else "?",
          flush=True)
