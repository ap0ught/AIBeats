"""Submit a job script to a running tools/s6_worker.py and print its output.

    python tools/s6_job.py <worker name> <script.py> [timeout seconds]
"""
import shutil
import sys
import time
from pathlib import Path

JOBDIR = Path(r"~\AppData\Local\Temp\claude\G--AI-World-Record\d5fcfe9d-4ac8-40d5-8a32-00e8e94fae89\scratchpad\s67\jobs")
name, script = sys.argv[1], Path(sys.argv[2])
timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 540
jid = f"{int(time.time() * 1000)}"
job = JOBDIR / f"{jid}.{name}.job.py"
tmp = JOBDIR / f"{jid}.{name}.tmp"
shutil.copyfile(script, tmp)
tmp.replace(job)
done = JOBDIR / f"{jid}.{name}.done"
out = JOBDIR / f"{jid}.{name}.out"
t0 = time.time()
while not done.exists():
    if time.time() - t0 > timeout:
        (JOBDIR / f"CANCEL_{name}").write_text("x")
        time.sleep(3)
        print(f"[timeout after {timeout} s; cancel requested for {job.name}]")
        break
    time.sleep(0.1)
txt = out.read_text(encoding="utf-8") if out.exists() else "(no output)"
print(txt[-int(sys.argv[4]):] if len(sys.argv) > 4 else txt)
