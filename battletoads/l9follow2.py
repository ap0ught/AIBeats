"""Terra Tubes follow-mode chain: each row = (bookmark, i_from, i_to, width, steps) follows the TAS's player-1 path
between two placement-anchored frame indices, starting from the previous row's solved state (its root height comes
from an l9.py replay of the solved rows). Rows with an existing json are skipped; a row whose search is running is
waited for.      python l9follow.py"""
import os, re, shutil, subprocess, sys, time
from pathlib import Path
P = Path(__file__).parent
ROWS = [
    ("L9_s3c", 375, 700, 400, 100),      # the tube's water line and the jump into the channel
    ("L9_s4c", 700, 1130, 400, 160),     # the pipe's interior (spark dodged by the 30-frame delay), the pool jumps, the land at (696,-42)
    ("L9_g3", 1130, 1500, 400, 160),     # the land: right along the pipes with the first cog
    ("L9_g4", 1500, 1900, 400, 160),
    ("L9_g5", 1900, 2300, 400, 160),
    ("L9_g6", 2300, 2700, 400, 160),
    ("L9_g7", 2700, 3100, 400, 160),
]
BASE = ["L9_s1", "L9_s1wait", "L9_s2b", "L9_s2wait"]                    # sections before the first follow row (s1wait: 30 idle frames in the water pocket)
done = list(BASE)
for bm, i0, i1, width, steps in ROWS:
    log = P / "logs" / f"l4s_{bm}.txt"; js = P / "knowledge" / f"l4s_{bm}.json"
    if js.exists() or i0 is None:
        done.append(bm); print(bm, "already solved" if i0 is not None else "scripted", flush=True); continue
    if log.exists() and not any(w in log.read_text() for w in ("solved", "unsolved")):
        print(bm, "running, waiting", flush=True)
        while not any(w in log.read_text() for w in ("solved", "unsolved")):
            time.sleep(20)
    else:
        out = subprocess.run([sys.executable, "l9.py", *done], cwd=P, capture_output=True, text=True).stdout
        hroot = int(re.findall(r"section \S+: \d+ frames -> f\d+ H (-?\d+)", out)[-1])
        shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
        print(f"{bm}: root H {hroot}, TAS {i0}->{i1}", flush=True)
        env = dict(os.environ, L4S_LVL="11", L4S_SAFE="20", L4S_STEPS=str(steps), L4S_ACTS="swim", L4S_FOLLOW=f"{i0},{i1}", L4S_HROOT=str(hroot))
        with open(log, "w") as f:
            subprocess.run([sys.executable, "l4s.py", bm, "0", "0", str(width), "follow"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
    txt = log.read_text()
    print(bm, [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved", "  GOAL"))][-2:], flush=True)
    if "unsolved" in txt:
        break
    done.append(bm)
