"""Job (worker): full stage 7 solves + replay checks from named states, results appended to
logs/s7/scan/<tag>.jsonl. Environment S7_SOLVE = "tag;state=name[:lead];state=name[:lead];..." """
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(r"")
sys.path.insert(0, str(ROOT / "tools"))
import s6_solve

spec = os.environ["S7_SOLVE"].split(";")
tag = spec[0]
for item in spec[1:]:
    st, name = item.split("=")
    lead = 0
    if ":" in name:
        name, lead = name.split(":")
        lead = int(lead)
    t0 = time.time()
    res, rows = s6_solve.run(sim, 7, st, name, {"lead_pause": lead} if lead else None, True,
                             log=lambda *a: print(*a, flush=True))
    fc = res.get("start_fc")
    rec = {"fc": (fc + lead) & 255 if fc is not None else None, "state": st, "lead": lead, "ok": res.get("ok"),
           "verified": res.get("verified"), "frames": (res.get("frames") - lead) if res.get("ok") else None,
           "rows": res.get("frames"), "lag": res.get("lag"), "result": res.get("result"),
           "check_inputs": res.get("check_inputs"), "deaths": res.get("deaths"), "remedies": res.get("remedies"),
           "local_fixes": res.get("local_fixes"), "marks": {m[0]: m[1] for m in res.get("marks", [])},
           "procs": res.get("procs"), "next_fc": (res.get("replay") or {}).get("next_frame", {}).get("fc"),
           "lead_seen": res.get("lead_pause_frames_seen"), "seconds": round(time.time() - t0),
           "name": name if st.startswith("s6/") or not name.startswith("scan_") else None}
    (ROOT / "logs" / "s7" / "scan").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "logs" / "s7" / "scan" / f"{tag}.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    print("RESULT", {k: rec[k] for k in ("fc", "state", "lead", "ok", "verified", "frames", "lag", "check_inputs", "seconds")},
          flush=True)
