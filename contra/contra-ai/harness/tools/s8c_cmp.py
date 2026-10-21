"""Compare finished stage 8 segments row by row at the level of events: A presses (jumps), B presses per 100 rows,
lag rows (from the report's verify block), the phase events.

    python tools/s8c_cmp.py <seg name under logs/> <seg name> ...
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import LOGS_DIR  # noqa: E402

for name in sys.argv[1:]:
    j = json.loads((LOGS_DIR / f"{name}.seg.json").read_text(encoding="utf-8"))
    rows = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
    rp = LOGS_DIR / f"{name}.report.json"
    rep = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}

    def st(b):
        return [i for i, r in enumerate(rows) if b in r and (i == 0 or b not in rows[i - 1])]
    a, b = st("A"), st("B")
    ev = rep.get("events", {})
    print(f"== {name}: rows {len(rows)}, events {ev}")
    print(f"   lag rows {rep.get('verify', {}).get('lag_frames')}")
    print(f"   A presses ({len(a)}): {a}")
    print(f"   B presses ({len(b)}) per 100 rows: " + " ".join(str(sum(1 for s in b if q <= s < q + 100)) for q in range(0, len(rows), 100)))
    for btn in ("Up", "Down", "Left"):
        s = st(btn)
        print(f"   {btn} presses ({len(s)}): {s[:40]}")
    nr = [i for i, r in enumerate(rows) if "Right" not in r and i < ev.get("boss_scroll", 0)]
    print(f"   rows without Right before the boss scroll: {len(nr)} {nr[:30]}")
