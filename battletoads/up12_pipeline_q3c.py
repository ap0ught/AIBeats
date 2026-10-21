"""Waits for the queen L13q3c (behind L12q3); then assembles up12c, builds the text and renders (2026-10-07)."""
import json, os, subprocess, sys, time
from toads.emulator import LOGS_DIR
p = LOGS_DIR / "pbeam_L13q3c.json"
while not p.exists():
    if os.path.exists("logs/l13solve_L13q3c.txt") and "unsolved" in open("logs/l13solve_L13q3c.txt").read(): print("L13q3c unsolved", flush=True); sys.exit(1)
    time.sleep(60)
time.sleep(5); n = len(json.load(open(p))["inputs"]); print("L13q3c", n, "(L13q3 1861)", flush=True)
if n >= 1861: print("not shorter than L13q3: no up12c", flush=True); sys.exit(0)
def run(args):
    print(">>", " ".join(args), flush=True); rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode; print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up12c", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10t", "L11r", "L12q3", "L13q3c"]): sys.exit(1)
run(["video_text2.py", "up12c"]); run(["render_overlay.py", "up12c"]); print("PIPELINE DONE", flush=True)
