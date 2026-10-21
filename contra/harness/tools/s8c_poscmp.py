"""Where two finished stage 8 segments gain or lose against each other: the row on which the scroll position
(screen * 256 + offset) first reaches every multiple of `step`, from the traces written by tools/s8c_trace.py.

    python tools/s8c_poscmp.py <trace json under logs/> <trace json under logs/> [step]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import LOGS_DIR  # noqa: E402

a = json.loads((LOGS_DIR / sys.argv[1]).read_text(encoding="utf-8"))
b = json.loads((LOGS_DIR / sys.argv[2]).read_text(encoding="utf-8"))
step = int(sys.argv[3]) if len(sys.argv) > 3 else 64


def reach(tr):
    out = {}
    for k, s in enumerate(tr):
        p = s["screen"] * 256 + s["scroll"]
        q = p // step * step
        if q not in out:
            out[q] = k
    return out


ra, rb = reach(a["trace"]), reach(b["trace"])
prev = 0
print("events A", a["events"], "lag", a["lag_rows"])
print("events B", b["events"], "lag", b["lag_rows"])
for q in sorted(set(ra) & set(rb)):
    d = rb[q] - ra[q]
    mark = "" if d == prev else f"   <-- {d - prev:+d}"
    print(f"pos {q:5d}: A row {ra[q]:5d}  B row {rb[q]:5d}  B-A {d:+4d}{mark}")
    prev = d
