"""Development driver for the dragon-mouth beam: python tools/s3_mouth_dev.py [name=v3] [M=2702] [--quick]"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, Ck  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR, Pad, check_rows  # noqa: E402
from contra.stages import s3_boss  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
name = args[0] if args else "v3"
M = int(args[1]) if len(args) > 1 else 2702
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / f"s3/{name}.seg.json").read_text())["rows"]]
i0 = M - 70
with Engine(int(args[2]) if len(args) > 2 else 3, tag="s3") as eng:
    ck = Ck(f"s3/s3_{name}_m70", i0, rows[:i0], Pad.from_rows(rows[:i0]))
    t0 = time.time()
    ck2 = s3_boss.beam_mouth(eng, ck, 0x13, M, quick="--quick" in sys.argv)
    if ck2 is None:
        print("beam failed")
    else:
        print(f"kill row {ck2.i - 1} ({ck2.i - 1 - M} after the opening at {M}); {time.time() - t0:.0f}s; violations",
              check_rows(ck2.rows))
        tr = eng.sim(ck, ck2.rows[i0:])
        print("lag rows in the fight:", sum(1 for z in tr if z["lagged"]), "x at kill", tr[-1]["x"])
        (LOGS_DIR / f"s3/p2_mouth_{name}.json").write_text(json.dumps({"i0": i0, "rows": ["+".join(r) for r in ck2.rows[i0:]]}))
