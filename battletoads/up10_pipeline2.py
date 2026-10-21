"""Waits for L12r (the fit behind the TAS Rat Race), stops the exploratory queen solve on L12d, runs two queen solves on L12r_end0
(default action set -> L13r, Select set -> L13rq) in parallel, keeps the shorter, assembles up10, builds the text, renders."""
import json, os, subprocess, sys, time
from toads.emulator import LOGS_DIR
while not (LOGS_DIR / "pbeam_L12r.json").exists(): time.sleep(30)
time.sleep(5)
subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*l13solve.py L12d_end0 0 L13q*' -or $_.CommandLine -like '*l4s.py L13q*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"])
print("L12r ready; queen q stopped; solving L13r and L13rq", flush=True)
p1 = subprocess.Popen([sys.executable, "-u", "l13solve.py", "L12r_end0", "0", "L13r"], stdout=open("logs/l13solve_r.txt", "w"), stderr=subprocess.STDOUT)
p2 = subprocess.Popen([sys.executable, "-u", "l13solve.py", "L12r_end0", "0", "L13rq"], stdout=open("logs/l13solve_rq.txt", "w"), stderr=subprocess.STDOUT, env=dict(os.environ, L4S_ACTS="queen"))
p1.wait(); p2.wait()
best = None
for name in ("L13r", "L13rq"):
    p = LOGS_DIR / f"pbeam_{name}.json"
    if p.exists():
        n = len(json.load(open(p))["inputs"]); print(name, n, "frames", flush=True)
        if best is None or n < best[0]: best = (n, name)
if best is None: print("no queen solved", flush=True); sys.exit(1)
print("using", best, flush=True)
def run(args):
    print(">>", " ".join(args), flush=True)
    rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode
    print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up10", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10t", "L11r", "L12r", best[1]]): sys.exit(1)
run(["video_text2.py", "up10"])
run(["render_overlay.py", "up10"])
print("PIPELINE DONE", flush=True)
