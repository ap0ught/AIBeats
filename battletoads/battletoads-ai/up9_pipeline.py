"""Waits for the queen (logs/pbeam_L13d.json), then assembles route up9 (two power-on replays, sha1 match), builds the video text and
renders the overlay video. Logs to logs/up9_pipeline.txt."""
import os, subprocess, sys, time
from toads.emulator import LOGS_DIR
while not (LOGS_DIR / "pbeam_L13d.json").exists(): time.sleep(30)
time.sleep(5)
def run(args):
    print(">>", " ".join(args), flush=True)
    rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode
    print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up9", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10c", "L11c", "L12d", "L13d"]): sys.exit(1)
run(["video_text2.py", "up9"])
run(["render_overlay.py", "up9"])
print("PIPELINE DONE", flush=True)
