"""Waits for the queen L13w6e; if shorter than L13w6 (1,830), assembles up12, builds the text and renders."""
import json, os, subprocess, sys, time
from toads.emulator import LOGS_DIR
p = LOGS_DIR / "pbeam_L13w6e.json"
while not p.exists():
    if os.path.exists("logs/l13solve_w6e.txt") and "unsolved" in open("logs/l13solve_w6b.txt").read(): print("w6e unsolved", flush=True); sys.exit(1)
    time.sleep(60)
time.sleep(5); n = len(json.load(open(p))["inputs"]); print("L13w6e", n, "(L13w6 1830)", flush=True)
if n >= 1830: print("not shorter: no up12", flush=True); sys.exit(0)
def run(args):
    print(">>", " ".join(args), flush=True); rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode; print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up12", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10t", "L11r", "L12r", "L13w6e"]): sys.exit(1)
run(["video_text2.py", "up12"]); run(["render_overlay.py", "up12"]); print("PIPELINE DONE", flush=True)
