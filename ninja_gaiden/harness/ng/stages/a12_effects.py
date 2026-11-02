"""Precompute effects_resolve caches (work/a12/effects_<stage>.json) for the given stages."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ng import legal
from ng.emulator import BizHawk
from run_stage import effects_for, stage_index

if __name__ == "__main__":
    ref = legal.TasRef()
    with BizHawk(log_name="a12_effects.log") as e:
        for n in sys.argv[1:]:
            effects_for(e, ref, stage_index(n), log=lambda m: print(m, flush=True))
