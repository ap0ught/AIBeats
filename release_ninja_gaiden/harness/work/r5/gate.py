"""Round 5 gate: wait until (EmuHawk + Mesen processes on the machine) < 3 (my own share), free RAM >= 2.5 GB and,
if a HOLD_FARMS file exists, none of my r5 emulators run; then run the command (output to the given log).
    python work/r5/gate.py <log> <cmd ...>"""
import os, subprocess, sys, time
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P))
from ng.fastcore import free_ram_gb  # noqa


def emus():
    out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True).stdout
    return sum(1 for l in out.splitlines() if l.startswith('"EmuHawk.exe"') or l.startswith('"Mesen.exe"'))


def hold():
    return any(p.exists() for p in [P / "logs/HOLD_FARMS", P.parent / "Contra/logs/HOLD_FARMS"])


log = sys.argv[1]
cmd = sys.argv[2:]
while True:
    n = emus()
    lim = 3
    if n < lim and free_ram_gb() >= 2.5 and not (hold() and n >= 1):
        break
    time.sleep(20 + (os.getpid() % 10))
with open(log, "w") as f:
    f.write(f"# gate passed {time.strftime('%H:%M:%S')} emus {n}\n")
    f.flush()
    r = subprocess.run(cmd, cwd=str(P), stdout=f, stderr=subprocess.STDOUT)
sys.exit(r.returncode)
