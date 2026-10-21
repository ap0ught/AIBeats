"""check_inputs.py on a rows file that has no .inputs.txt yet (a rooms-only solve):

    python tools/s4t_check_rows.py <stage> <tag> [history inputs file]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.inputs import read_inputs, write_inputs  # noqa: E402

stage, tag = sys.argv[1], sys.argv[2]
hist = sys.argv[3] if len(sys.argv) > 3 else None
rows = [tuple(r) for r in json.loads((ROOT / "logs" / f"s{stage}" / f"{tag}_rows.json").read_text())]
chk = (list(read_inputs(ROOT / hist))[-1800:] if hist else []) + rows
tmp = ROOT / "logs" / f"s{stage}" / f"{tag}_chk.inputs.txt"
write_inputs(tmp, chk, "check: history tail + rows")
cp = subprocess.run([sys.executable, str(ROOT / "check_inputs.py"), str(tmp)], capture_output=True, text=True)
print(cp.stdout[-1800:])
print("exit", cp.returncode)
tmp.unlink()
