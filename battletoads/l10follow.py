"""Rat Race follow chain on the 1-player TAS path (tas/watch_1p_l10.txt, placement (88,158)): 300-index follow
sections, then a final section whose goal is the rat booted (hp 0).      python l10follow.py"""
import os, re, shutil, subprocess, sys, time
from pathlib import Path
P = Path(__file__).parent
ROWS = [(f"L10_f{k}", 300 * (k - 1), 300 * k, 400, 200, 4, {}) for k in range(1, 5)]         # 0 .. 1200
ROWS += [("L10_f5", 1200, 1320, 400, 200, 4, {"L4S_BOMBDONE": "1", "L4S_AIRB": "1"}),                          # land, kick the bomb
         ("L10_f6", 1320, 1600, 400, 200, 4, {"L4S_RATDEAD": "1", "L4S_AIRB": "1", "L4S_FORBID": "0,300,-3500,-3210"})]                           # hard hit + boot
done = []
for bm, i0, i1, width, steps, macro, extra in ROWS:
    log = P / "logs" / f"l4s_{bm}.txt"; js = P / "knowledge" / f"l4s_{bm}.json"
    if js.exists():
        done.append(bm); print(bm, "already solved", flush=True); continue
    if done:
        out = subprocess.run([sys.executable, "l10.py", *done], cwd=P, capture_output=True, text=True).stdout
        hroot = int(re.findall(r"section \S+: \d+ frames -> f\d+ H (-?\d+)", out)[-1])
        shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
    else:
        hroot = 0
        shutil.copy(P / "states" / "L10_start.State", P / "states" / f"{bm}.State")
    print(f"{bm}: root H {hroot}, 1P TAS {i0}->{i1}", flush=True)
    env = dict(os.environ, L4S_LVL="9", L4S_SAFE="20", L4S_STEPS=str(steps), L4S_FOLLOW=f"{i0},{i1}", L4S_HROOT=str(hroot),
               L4S_TASLOG="tas/watch_1p_l10.txt", L4S_PLACE="88,158", L4S_MACRO=str(macro), **extra)
    with open(log, "w") as f:
        subprocess.run([sys.executable, "l4s.py", bm, "0", "0", str(width), "follow"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
    txt = log.read_text()
    print(bm, [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved", "  GOAL"))][-2:], flush=True)
    if "unsolved" in txt:
        break
    done.append(bm)
