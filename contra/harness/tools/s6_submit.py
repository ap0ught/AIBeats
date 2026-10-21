"""Submit a job script to a running tools/s6_worker.py without waiting; prints the output file path.

    python tools/s6_submit.py <worker name> <script.py> [tag]
"""
import shutil
import sys
import time
from pathlib import Path

JOBDIR = Path(r"~\AppData\Local\Temp\claude\G--AI-World-Record\d5fcfe9d-4ac8-40d5-8a32-00e8e94fae89\scratchpad\s67\jobs")
name, script = sys.argv[1], Path(sys.argv[2])
tag = sys.argv[3] if len(sys.argv) > 3 else script.stem
jid = f"{tag}_{int(time.time())}"
job = JOBDIR / f"{jid}.{name}.job.py"
tmp = JOBDIR / f"{jid}.{name}.tmp"
shutil.copyfile(script, tmp)
tmp.replace(job)
print(JOBDIR / f"{jid}.{name}.out")
