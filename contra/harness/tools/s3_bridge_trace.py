"""Trace Bill, the two bridge flames and the rocks along a finished segment (read-only replay).
    python tools/s3_bridge_trace.py <state> <seg.json> <row_from> <row_to> [step]"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR  # noqa: E402

state, seg, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
step = int(sys.argv[5]) if len(sys.argv) > 5 else 4
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / seg).read_text())["rows"]]
with Engine(1, tag="s3") as eng:
    tr = eng.sim(eng.root(state), rows[:b])
    seen = {}
    for i in range(a, min(b, len(tr))):
        s = tr[i]
        A = s["screen"] * 240 + s["scroll"]
        en = [(k, s[f"t{k}"], s[f"ex{k}"], s[f"ey{k}"]) for k in range(16) if s[f"r{k}"] and s[f"t{k}"] in (0x10, 0x11)]
        for k, t, x, y in en:
            if (k, t) not in seen:
                seen[(k, t)] = i
                print(f"   NEW type {t:02x} slot {k} at row {i}: x {x} y {y} A {A}")
        if (i - a) % step == 0:
            print(f"{i:5d} {'+'.join(rows[i]):12s} x{s['x']:4d} y{s['y']:4d} j{s['jump']:02x} A{A:5d} sub{s['sub']:02x} on{s['onenemy']} "
                  f"fc{s['fc']:3d} | " + " ".join(f"{t:02x}:{x},{y}" for k, t, x, y in en))
