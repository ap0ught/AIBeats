"""Waits for the queen solves L13r and L13rq (either may fail); when one exists and the other has finished or failed, takes the shorter,
assembles up10, builds the text, renders."""
import json, os, subprocess, sys, time
from toads.emulator import LOGS_DIR
def done(name): return (LOGS_DIR / f"pbeam_{name}.json").exists()
def failed(name):
    p = f"logs/l13solve_{name[3:]}.txt" if False else f"logs/l13solve_{'r' if name == 'L13r' else 'rq'}.txt"
    return os.path.exists(p) and "unsolved" in open(p).read()
while True:
    a, b = done("L13r") or failed("L13r"), done("L13rq") or failed("L13rq")
    if (done("L13r") or done("L13rq")) and a and b: break
    time.sleep(60)
best = None
for name in ("L13r", "L13rq"):
    if done(name):
        n = len(json.load(open(LOGS_DIR / f"pbeam_{name}.json"))["inputs"]); print(name, n, flush=True)
        if best is None or n < best[0]: best = (n, name)
print("using", best, flush=True)
def run(args):
    print(">>", " ".join(args), flush=True); rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode; print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up10", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10t", "L11r", "L12r", best[1]]): sys.exit(1)
run(["video_text2.py", "up10"]); run(["render_overlay.py", "up10"]); print("PIPELINE DONE", flush=True)
