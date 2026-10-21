"""Job: make stage 7 phase start states (title-screen delays) that the scan needs: states/s7/ph<d>.State."""
import sys
from pathlib import Path

ROOT = Path(r"")
sys.path.insert(0, str(ROOT / "tools"))
import s6_mk_phase

for d in (100, 95, 80):
    if (ROOT / "states" / "s7" / f"ph{d}.State").exists():
        print("exists", d)
        continue
    print(s6_mk_phase.make(sim.e, 7, d), flush=True)
sim.e.trace(True)
