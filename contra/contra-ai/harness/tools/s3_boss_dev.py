"""Development driver for the stage 3 boss phases, starting from a saved climb.

    python tools/s3_boss_dev.py <climb name, e.g. s3/dev3> [emus=3]
Reads logs/<name>_climb.rows.json and states/<name>_climb_end.State.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Pad, LOGS_DIR  # noqa: E402
from contra.stages.s3s8_engine import Engine, Ck  # noqa: E402
from contra.stages import s3_boss  # noqa: E402

name = sys.argv[1]
emus = int(sys.argv[2]) if len(sys.argv) > 2 else 3
j = json.loads((LOGS_DIR / f"{name}_climb.rows.json").read_text())
rows = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
eng = Engine(emus, tag=name.replace("/", "_"))
try:
    ck = Ck(f"{name}_climb_end", len(rows), rows, Pad.from_rows(rows))
    out = s3_boss.solve_boss(eng, ck, 0x13, name.replace("/", "_"))
    print(out[-1])
finally:
    eng.close()
