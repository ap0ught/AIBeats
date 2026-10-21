"""check_inputs.py on a stage 6 segment followed by the stage 7 segment solved from its end state (the press cap
applies across the stage boundary).

    python tools/s7_check_chain.py <s6 run in logs/s6> <s7 run in logs/s7>
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.inputs import read_inputs, write_inputs  # noqa: E402

a, b = sys.argv[1:3]
r6 = read_inputs(ROOT / "logs" / "s6" / f"{a}.inputs.txt")
r7 = read_inputs(ROOT / "logs" / "s7" / f"{b}.inputs.txt")
out = ROOT / "logs" / "s7" / f"chain_{a}__{b}.inputs.txt"
write_inputs(out, r6 + r7, f"stage 6 {a} ({len(r6)}) + stage 7 {b} ({len(r7)})")
print("stage 6", len(r6), "+ stage 7", len(r7), "=", len(r6) + len(r7), "; last stage 6 rows:", r6[-6:], "first stage 7 rows:", r7[:3])
res = subprocess.run([sys.executable, str(ROOT / "check_inputs.py"), str(out)], capture_output=True, text=True)
print(res.stdout.strip().splitlines()[-1])
