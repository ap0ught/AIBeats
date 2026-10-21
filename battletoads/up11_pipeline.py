"""Waits for the wide Select-set queen (L13w6) or the width-400 Select solve (L13rq); if the best is shorter than L13y (1,892 inputs),
assembles up11, builds the text and renders."""
import json, os, subprocess, sys, time
from toads.emulator import LOGS_DIR
def n(name): p = LOGS_DIR / f"pbeam_{name}.json"; return len(json.load(open(p))["inputs"]) if p.exists() else None
def failed(tag): p = f"logs/l13solve_{tag}.txt"; return os.path.exists(p) and "unsolved" in open(p).read()
while True:
    fin = {k: (n(k) is not None or failed(t)) for k, t in (("L13w6", "w6"), ("L13rq", "rq"))}
    if all(fin.values()): break
    time.sleep(60)
cands = [(n(k), k) for k in ("L13w6", "L13rq") if n(k) is not None]
print("queens:", cands, "current L13y", n("L13y"), flush=True)
if not cands or min(cands)[0] >= n("L13y"): print("no shorter queen: no up11", flush=True); sys.exit(0)
best = min(cands)[1]
def run(args):
    print(">>", " ".join(args), flush=True); rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode; print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up11", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10t", "L11r", "L12r", best]): sys.exit(1)
run(["video_text2.py", "up11"]); run(["render_overlay.py", "up11"]); print("PIPELINE DONE", flush=True)
