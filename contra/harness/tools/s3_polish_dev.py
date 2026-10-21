"""Development driver: greedy mouth fight + polish from a saved m70 state: python tools/s3_polish_dev.py [name=v3] [M=2702] [emus=1]"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, Ck  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR, Pad, check_rows  # noqa: E402
from contra.stages import s3_boss  # noqa: E402
from contra.stages.s8 import greedy_fight  # noqa: E402

args = sys.argv[1:]
name = args[0] if args else "v3"
M = int(args[1]) if len(args) > 1 else 2702
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / f"s3/{name}.seg.json").read_text())["rows"]]
i0 = M - 70
with Engine(int(args[2]) if len(args) > 2 else 1, tag="s3") as eng:
    ck0 = Ck(f"s3/s3_{name}_m70", i0, rows[:i0], Pad.from_rows(rows[:i0]))
    t0 = time.time()
    ck = greedy_fight(eng, ck0, 0x13, s3_boss.MOUTH, "M1", base=(), hp_fn=s3_boss.mouth_hp, heart=True,
                      progs=(("U", "U", "U"),), first_land_after=M + 4, first_credit=20, hp_full=32, maxseg=12)
    print(f"greedy: dead at row {ck.i - 1} ({ck.i - 1 - M} after the opening) {time.time() - t0:.0f}s")
    ck2 = s3_boss.polish_mouth(eng, ck0, ck, 0x13, 480)
    print(f"polished: dead at row {ck2.i - 1} ({ck2.i - 1 - M} after the opening) {time.time() - t0:.0f}s; violations",
          check_rows(ck2.rows))
    tr = eng.sim(ck0, ck2.rows[i0:])
    print("lag rows in the fight:", sum(1 for z in tr if z["lagged"]))
