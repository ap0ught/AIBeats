"""Replay a rows json from a state and list the lag frames (row index, scroll, live enemy slots, bullets).

    python tools/s3_lagscan.py <rows.json> [state=dbg/s3_pre]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402
from contra.inputs import to_mask  # noqa: E402

rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(sys.argv[1]).read_text())]
state = sys.argv[2] if len(sys.argv) > 2 else "dbg/s3_pre"
with Game(log_name="s3_lagscan.log") as g:
    r = g.load(state)
    lags = []
    prevA = 0
    for i, row in enumerate(rows):
        g.e.cmd("stepx " + f"{to_mask(row):02x}")
        r = g.read()
        A = r.screen * 240 + r.scroll
        if r.lagged:
            lags.append(i)
            print(f"lag row {i}: A={A} (dA {A - prevA}) enemies {len(r.enemies())} bullets {r.nbul()} fc={r.fc} y={r.y} "
                  f"vy={r.vy} $1b={r.m[0x1B]}")
        prevA = A
    print("lag frames:", len(lags), lags)
    print(r.desc())
