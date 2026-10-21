"""Job (worker): (1) replay stage 6 + stage 7 chains as one input list (tools/s7_j_chainreplay.py);
(2) stage 6 solved by the LIVE solver from the real chain state (chain1's s6_pre, copied to
states/s6/real_c1_s6_pre) - the state from which the boss beam used to die to its last line."""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(r"")
sys.path.insert(0, str(ROOT / "tools"))
os.environ["S7_CHAIN"] = "s6/ph66|final_ph66|f_chain66;s6/ph100|ph100|f_chain100"
exec(compile(open(ROOT / "tools" / "s7_j_chainreplay.py", encoding="utf-8").read(), "s7_j_chainreplay.py", "exec"))
import s6_solve

t0 = time.time()
res, rows = s6_solve.run(sim, 6, "s6/real_c1_s6_pre", "real_c1_live", None, True, log=lambda *a: print(*a, flush=True))
print("STAGE6 REAL", json.dumps({k: res.get(k) for k in ("ok", "result", "frames", "lag", "deaths", "verified", "check_inputs",
                                                        "start_fc", "weapon_out")}), "seconds", round(time.time() - t0), flush=True)
