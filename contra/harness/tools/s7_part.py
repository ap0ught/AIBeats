"""Submit a partial stage 7 solve (tools/s7_j_part.py) to a worker and print its output.

    python tools/s7_part.py <worker> <state> <row0> <tag> <parts> [k=v,k=v] [timeout s] [nowait]
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
worker, state, row0, tag, parts = sys.argv[1:6]
params = sys.argv[6] if len(sys.argv) > 6 else ""
timeout = sys.argv[7] if len(sys.argv) > 7 else "540"
nowait = len(sys.argv) > 8
scratch = Path(r"~\AppData\Local\Temp\claude\G--AI-World-Record\d5fcfe9d-4ac8-40d5-8a32-00e8e94fae89\scratchpad\s7b")
scratch.mkdir(parents=True, exist_ok=True)
job = scratch / f"part_{tag}.py"
job.write_text(
    "import os\n"
    f"os.environ.update(S7_STATE={state!r}, S7_ROW0={row0!r}, S7_TAG={tag!r}, S7_PARTS={parts!r}, S7_PARAMS={params!r})\n"
    f"exec(compile(open(r'{ROOT / 'tools' / 's7_j_part.py'}', encoding='utf-8').read(), 's7_j_part.py', 'exec'))\n",
    encoding="utf-8")
args = [sys.executable, str(ROOT / "tools" / "s7_job.py"), worker, str(job)]
args += ["nowait", tag] if nowait else [timeout, "6000"]
print(subprocess.run(args, capture_output=True, text=True).stdout)
