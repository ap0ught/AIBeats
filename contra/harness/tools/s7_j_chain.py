"""Job (worker): stage 7 solved from the states that stage 6 segments end in (real chains), one after another.
Results: logs/s7/c7_<s6 run>.seg.json / .inputs.txt and a line in logs/s7/scan/chains.jsonl."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(r"")
sys.path.insert(0, str(ROOT / "tools"))
import s6_solve

for run6 in ("ph100", "ph1", "ph70"):
    t0 = time.time()
    res, rows = s6_solve.run(sim, 7, f"s6/{run6}_end", f"c7_{run6}", None, True, log=lambda *a: print(*a, flush=True))
    rec = {"fc": res.get("start_fc"), "state": f"s6/{run6}_end", "lead": 0, "ok": res.get("ok"),
           "verified": res.get("verified"), "frames": res.get("frames") if res.get("ok") else None,
           "rows": res.get("frames"), "lag": res.get("lag"), "result": res.get("result"),
           "check_inputs": res.get("check_inputs"), "deaths": res.get("deaths"), "remedies": res.get("remedies"),
           "local_fixes": res.get("local_fixes"), "marks": {m[0]: m[1] for m in res.get("marks", [])},
           "procs": res.get("procs"), "next_fc": (res.get("replay") or {}).get("next_frame", {}).get("fc"),
           "seconds": round(time.time() - t0), "name": f"c7_{run6}"}
    (ROOT / "logs" / "s7" / "scan").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "logs" / "s7" / "scan" / "chains.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    print("RESULT", {k: rec[k] for k in ("fc", "state", "ok", "verified", "frames", "lag", "check_inputs", "seconds")}, flush=True)
