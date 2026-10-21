"""Clinger-Winger follow chain on the 1-player TAS path (tas/watch_1p_l11.txt, placement (28,44), height = -camy): 300-index follow
sections, then a final section whose goal is the rat booted (hp 0).      python l10follow.py"""
import os, re, shutil, subprocess, sys, time
from pathlib import Path
P = Path(__file__).parent
ROWS = [("L11_c1", 0, 5158, 0, 0, 4, {})]                    # (scripted greedy ride, l11greedy.py)
ROWS += [("L11_c2", 5158, 5480, 400, 200, 4, {"L4S_ACTS": ""}),   # the last straight, off the unicycle, into the arena
         ("L11_c3", 5480, 5645, 200, 100, 4, {"L4S_ACTS": ""}),   # the arrival animation until the Buzzball (0x7b) appears
         ("L11_c4", 5645, 6400, 400, 250, 4, {"L4S_ACTS": "", "L4S_RATDEAD": "1", "L4S_FOEID": "0x7b", "L4S_AIRB": "1"}),  # the fight (hp 207 -> 47)
         ("L11_c5", 6000, 6400, 400, 250, 4, {"L4S_ACTS": "", "L4S_RATDEAD": "1", "L4S_FOEID": "0x7b", "L4S_AIRB": "1"})]  # the fight (47 -> 0)
done = []
for bm, i0, i1, width, steps, macro, extra in ROWS:
    log = P / "logs" / f"l4s_{bm}.txt"; js = P / "knowledge" / f"l4s_{bm}.json"
    if js.exists():
        done.append(bm); print(bm, "already solved", flush=True); continue
    if done:
        out = subprocess.run([sys.executable, "l11.py", *done], cwd=P, capture_output=True, text=True).stdout
        hroot = int(re.findall(r"section \S+: \d+ frames -> f\d+ H (-?\d+)", out)[-1])
        shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
    else:
        hroot = 0
        shutil.copy(P / "states" / "L11_start.State", P / "states" / f"{bm}.State")
    print(f"{bm}: root H {hroot}, 1P TAS {i0}->{i1}", flush=True)
    env = dict(os.environ, L4S_LVL="10", L4S_HCAM="1", L4S_SAFE="20", L4S_STEPS=str(steps), L4S_FOLLOW=f"{i0},{i1}", L4S_HROOT=str(hroot),
               L4S_TASLOG="tas/watch_1p_l11.txt", L4S_PLACE="28,44", L4S_MACRO=str(macro))
    env.update({"L4S_ACTS": "dpad"}); env.update(extra)
    with open(log, "w") as f:
        subprocess.run([sys.executable, "l4s.py", bm, "0", "0", str(width), "follow"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
    txt = log.read_text()
    print(bm, [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved", "  GOAL"))][-2:], flush=True)
    if "unsolved" in txt:
        break
    done.append(bm)
