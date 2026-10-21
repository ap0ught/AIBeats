"""Chain climb searches up Intruder Excluder: wait for section <first> to finish (if it is already running),
then start each next section from the previous one's solved state.

    python l8climb.py <prefix c|p> <script l4s.py|l4sp.py> <first> <last> [step_px]
"""
import os, subprocess, sys, time, shutil
from pathlib import Path
P = Path(__file__).parent
prefix, script, first, last = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
step_px = int(sys.argv[5]) if len(sys.argv) > 5 else 600
tag = "l4sp" if script == "l4sp.py" else "l4s"
for i in range(first, last + 1):
    log = P / "logs" / f"{tag}_L8_{prefix}{i}.txt"
    if i == first and log.exists():                  # section already running (launched by hand): wait for it
        while not any(w in log.read_text() for w in ("solved", "unsolved")):
            time.sleep(20)
    else:
        shutil.copy(P / "states" / f"L8_{prefix}{i-1}_solved.State", P / "states" / f"L8_{prefix}{i}.State")
        env = dict(os.environ, L4S_LVL="7", L4S_SAFE="30", L4S_STEPS="200", L4S_ACTS="climb", L4S_WORKERS=os.environ.get("L4S_WORKERS", "3"))
        with open(log, "w") as f:
            subprocess.run([sys.executable, script, f"L8_{prefix}{i}", "0", str(step_px), "600", "climb"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
    txt = log.read_text()
    print(f"{prefix}{i}:", [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved", "  GOAL"))][-2:], flush=True)
    if "unsolved" in txt:
        break
