"""Round 4: run work/r4/astar.py leg by leg (each leg's rows = the next leg's prefix), one emulator at a time.
    python work/r4/chainrooms.py <stage> <start state> <first prefix|-> <tag> <goal1> <goal2> ... [--w 1.4] [--max-exp N]
Legs write logs/r4/<tag>_<k>.inputs.txt and logs/r4/<tag>_<k>.out. Stops at the first leg without a goal.
Env flags A34_AIRRUN/HMAX/SWITCH are set to 1 (A34_THROW too if --throw)."""
import os
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
        return v
    return d


w = opt("--w", "1.4")
mx = opt("--max-exp", "1200")
throw = "--throw" in a
if throw:
    a.remove("--throw")
stage, start, prefix, tag = a[:4]
goals = a[4:]
env = dict(os.environ, A34_AIRRUN="1", A34_HMAX="1", A34_SWITCH="1")
if throw:
    env["A34_THROW"] = "1"
for k, g in enumerate(goals):
    out = f"{tag}_{k}"
    log = P / "logs" / "r4" / f"{out}.out"
    cmd = [sys.executable, "-u", str(P / "work/r4/astar.py"), stage, start, prefix, g, out, "--w", w, "--max-exp", mx]
    print("leg", k, " ".join(cmd[2:]), flush=True)
    with open(log, "w") as f:
        rc = subprocess.run(cmd, cwd=str(P), env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    txt = log.read_text()
    res = [l for l in txt.splitlines() if l.startswith("RESULT")]
    print("leg", k, "rc", rc, res[-1] if res else "NO GOAL", flush=True)
    if not res:
        break
    prefix = out
