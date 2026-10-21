"""Trace a stage 7 segment on a worker, then print the section table and stalls.

    python tools/s7_tr.py <worker> <state> <name> [from_row]
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
worker, state, name = sys.argv[1:4]
scratch = Path(r"~\AppData\Local\Temp\claude\G--AI-World-Record\d5fcfe9d-4ac8-40d5-8a32-00e8e94fae89\scratchpad\s7b")
job = scratch / f"trace_{name}.py"
job.write_text("import os\n" + f"os.environ['S7_TRACE'] = {state + '|' + name!r}\n"
               + f"exec(compile(open(r'{ROOT / 'tools' / 's7_j_trace.py'}', encoding='utf-8').read(), 's7_j_trace.py', 'exec'))\n",
               encoding="utf-8")
print(subprocess.run([sys.executable, str(ROOT / "tools" / "s7_job.py"), worker, str(job), "300", "1500"],
                     capture_output=True, text=True).stdout)
import json
tr = json.loads((ROOT / "logs" / "s7" / f"{name}.trace.json").read_text())
lo = int(sys.argv[4]) if len(sys.argv) > 4 else 0
i = lo
n = len(tr)
print("stalls (camera unchanged >= 3 rows) from row", lo)
while i < n:
    j = i
    while j + 1 < n and tr[j + 1][0] == tr[i][0]:
        j += 1
    if j - i >= 2 and tr[i][13] == 4 and tr[i][0] < 3584:
        seg = tr[i:j + 1]
        print(f"  row {i:5d} len {j - i + 1:4d} cam {tr[i][0]:5d} (wx {tr[i][0] + seg[0][1]}) y {seg[0][2]}..{seg[-1][2]} "
              f"lag {sum(r[4] for r in seg)} pause {sum(1 for r in seg if r[5])} fc {seg[0][3]}")
    i = j + 1
