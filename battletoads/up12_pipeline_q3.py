"""Waits for the queen L13q3 (behind L12q3); then assembles up12, builds the text and renders (2026-10-07)."""
import json, os, subprocess, sys, time
from toads.emulator import LOGS_DIR
p = LOGS_DIR / "pbeam_L13q3.json"
while not p.exists():
    if os.path.exists("logs/l13solve_L13q3.txt") and "unsolved" in open("logs/l13solve_L13q3.txt").read(): print("L13q3 unsolved", flush=True); sys.exit(1)
    time.sleep(60)
time.sleep(5); n = len(json.load(open(p))["inputs"]); print("L13q3", n, "(L13w6 1830)", flush=True)
def run(args):
    print(">>", " ".join(args), flush=True); rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode; print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up12", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10t", "L11r", "L12q3", "L13q3"]): sys.exit(1)
run(["video_text2.py", "up12"]); run(["render_overlay.py", "up12"]); print("PIPELINE DONE", flush=True)
