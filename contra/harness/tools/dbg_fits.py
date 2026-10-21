"""DEBUG states: fit the Mars608 movie's outdoor stages from poked stage-start states, one after the other.
    python tools/dbg_fits.py 3:7327 5:15049 ...
Per stage: logs/dbg/mars_s<k>.seg.json, log to stdout."""
import subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
for spec in sys.argv[1:]:
    k, m = spec.split(":")
    print(f"===== stage {k} m={m}", flush=True)
    subprocess.run([sys.executable, "-u", str(root / "tools" / "repair.py"), f"dbg/s{k}_pre",
                    str(root / "logs" / "tas_4623M_raw.inputs.txt"), m, f"dbg/mars_s{k}"], cwd=str(root))
