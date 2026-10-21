"""Submit full stage 7 solves to a worker (no waiting).

    python tools/s7_solve_w.py <worker> <tag> <state=name[:lead]> [<state=name[:lead]> ...]
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
worker, tag = sys.argv[1:3]
items = sys.argv[3:]
scratch = Path(r"~\AppData\Local\Temp\claude\G--AI-World-Record\d5fcfe9d-4ac8-40d5-8a32-00e8e94fae89\scratchpad\s7b")
job = scratch / f"solve_{tag}_{worker}.py"
spec = ";".join([tag] + items)
job.write_text("import os\n" + f"os.environ['S7_SOLVE'] = {spec!r}\n"
               + f"exec(compile(open(r'{ROOT / 'tools' / 's7_j_solve1.py'}', encoding='utf-8').read(), 's7_j_solve1.py', 'exec'))\n",
               encoding="utf-8")
print(subprocess.run([sys.executable, str(ROOT / "tools" / "s7_job.py"), worker, str(job), "nowait", f"solve_{tag}"],
                     capture_output=True, text=True).stdout)
