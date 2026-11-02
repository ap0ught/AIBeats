"""l53b gate: wait until free RAM >= need (1.5 GB if no other l53b Mesen job runs, else 3.0 GB) and < 3 l53b jobs run, then run.
python work/l53b/g.py <log> <cmd ...>"""
import os, subprocess, sys, time
sys.path.insert(0, '.')
from ng.fastcore import free_ram_gb
def mine():
    out = subprocess.run(['powershell', '-NoProfile', '-Command',
        "(Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | ? { $_.CommandLine -like '*work/l53b/*' -and $_.CommandLine -notlike '*g.py*' }).Count"],
        capture_output=True, text=True).stdout.strip()
    return int(out or 0)
log, cmd = sys.argv[1], sys.argv[2:]
t0 = time.time()
while True:
    n = mine(); fr = free_ram_gb()
    if n < 3 and fr >= (1.6 if n == 0 else 2.5): break
    time.sleep(15)
with open(log, 'w') as f:
    f.write(f"# gate passed {time.strftime('%H:%M:%S')} waited {time.time()-t0:.0f}s\n"); f.flush()
    r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
sys.exit(r.returncode)
