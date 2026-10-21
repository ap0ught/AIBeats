"""Waits for the queen variant L13f; if its segment is shorter than L13d's, assembles route up10 with it, builds the video text and renders."""
import json, os, subprocess, sys, time
from toads.emulator import LOGS_DIR
while not (LOGS_DIR / "pbeam_L13f.json").exists(): time.sleep(30)
time.sleep(5)
nd = len(json.load(open(LOGS_DIR / "pbeam_L13d.json"))["inputs"]); nf = len(json.load(open(LOGS_DIR / "pbeam_L13f.json"))["inputs"])
print("L13d", nd, "frames; L13f", nf, "frames", flush=True)
if nf >= nd: print("L13f is not shorter: no up10", flush=True); sys.exit(0)
def run(args):
    print(">>", " ".join(args), flush=True)
    rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode
    print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up10", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10c", "L11c", "L12d", "L13f"]): sys.exit(1)
run(["video_text2.py", "up10"])
run(["render_overlay.py", "up10"])
print("PIPELINE DONE", flush=True)
