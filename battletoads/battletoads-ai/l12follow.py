"""The Revolution follow chain on the 1-player TAS path (tas/watch_1p_l12.txt, placement (136,30), x wraps at 512): 300-index follow
sections, then a final section whose goal is the rat booted (hp 0).      python l10follow.py"""
import os, re, shutil, subprocess, sys, time
from pathlib import Path
P = Path(__file__).parent
ROWS = [(f"L12_r{k}", 300 * (k - 1), 300 * k, 400, 200, 4, {}) for k in range(1, 26)]     # to index 7500
done = []
for bm, i0, i1, width, steps, macro, extra in ROWS:
    log = P / "logs" / f"l4s_{bm}.txt"; js = P / "knowledge" / f"l4s_{bm}.json"
    if js.exists():
        done.append(bm); print(bm, "already solved", flush=True); continue
    if done:
        out = subprocess.run([sys.executable, "l12.py", *done], cwd=P, capture_output=True, text=True).stdout
        hroot = int(re.findall(r"section \S+: \d+ frames -> f\d+ H (-?\d+)", out)[-1])
        shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
    else:
        hroot = 0
        shutil.copy(P / "states" / "L12_start.State", P / "states" / f"{bm}.State")
    print(f"{bm}: root H {hroot}, 1P TAS {i0}->{i1}", flush=True)
    env = dict(os.environ, L4S_LVL="5", L4S_XWRAP="512", L4S_ACTS="rev", L4S_AIRB="1", L4S_SAFE="20", L4S_STEPS=str(steps), L4S_FOLLOW=f"{i0},{i1}", L4S_HROOT=str(hroot),
               L4S_TASLOG="tas/watch_1p_l12.txt", L4S_PLACE="136,30", L4S_MACRO=str(macro), **extra)
    with open(log, "w") as f:
        subprocess.run([sys.executable, "l4s.py", bm, "0", "0", str(width), "follow"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
    txt = log.read_text()
    print(bm, [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved", "  GOAL"))][-2:], flush=True)
    if "unsolved" in txt:
        break
    done.append(bm)
