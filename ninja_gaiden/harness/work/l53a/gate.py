"""l53a gate: wait until free RAM >= 3.0 GB and (Mesen + EmuHawk processes, minus the dead PID 26268) < LIM, then run cmd.
python work/l53a/gate.py [--lim N] <log|-> <cmd ...>"""
import os, subprocess, sys, time
sys.path.insert(0, '.')
from ng.fastcore import free_ram_gb
a = sys.argv[1:]
LIM = 6; MIN = 3.0
while a[0] in ('--lim', '--min'):
    if a[0] == '--lim': LIM = int(a[1])
    else: MIN = float(a[1])
    a = a[2:]
def emus():
    out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True).stdout
    return sum(1 for l in out.splitlines() if (l.startswith('"EmuHawk.exe"') or l.startswith('"Mesen.exe"')) and '"26268"' not in l)
t0 = time.time()
while not (free_ram_gb() >= MIN and emus() < LIM):
    time.sleep(10)
log, cmd = a[0], a[1:]
if log == '-':
    r = subprocess.run(cmd)
else:
    with open(log, 'w') as f:
        f.write(f"# gate passed {time.strftime('%H:%M:%S')} waited {time.time()-t0:.0f}s\n"); f.flush()
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
sys.exit(r.returncode)
