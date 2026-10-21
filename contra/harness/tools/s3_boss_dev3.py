"""Development: the dragon's mouth from a saved state 70 rows before it opens (arms alive).
    python tools/s3_boss_dev3.py <climb name> [xs comma list] [emus=1]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Pad, LOGS_DIR  # noqa: E402
from contra.stages.s3s8_engine import Engine, Ck, gen, new_ov  # noqa: E402
from contra.stages import s3_boss  # noqa: E402
from contra.stages.s8 import greedy_fight, log  # noqa: E402

name = sys.argv[1]
xs = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [123]
emus = int(sys.argv[3]) if len(sys.argv) > 3 else 1
j = json.loads((LOGS_DIR / f"{name}_m70.rows.json").read_text())
rows = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
m_open = j["m_open"]
eng = Engine(emus, tag=name.replace("/", "_"))
try:
    ck0 = Ck(f"{name}_m70", len(rows), rows, Pad.from_rows(rows))
    x0 = eng.sim(ck0, [()])[0]["x"]
    print("x0", x0, "ck0.i", ck0.i, "m_open", m_open)
    for xt in xs:
        o = new_ov()
        dx = xt - 2 - x0
        o["holds"].append((ck0.i, ck0.i + abs(dx), "Right" if dx > 0 else "Left"))
        o["holds"].append((ck0.i + abs(dx) + 2, ck0.i + abs(dx) + 4, "Right"))
        rr = gen(ck0.pad, ck0.i, 50, o, base=(), fire=False)[0]
        ckf, tr = eng.commit(ck0, rr)
        print("X target", xt, "reached", tr[-1]["x"], "at row", ckf.i, flush=True)
        taps = [None, (0, 11), (0, 14), (2, 12), (4, 12), (8, 12), (12, 12), (16, 12)]
        try:
            ckd = greedy_fight(eng, ckf, 0x13, s3_boss.MOUTH, f"M-x{xt}", base=(), hp_fn=s3_boss.mouth_hp, heart=True,
                               progs=(("U", "U", "U"),), first_land_after=m_open + 4, first_credit=20, hp_full=32,
                               maxseg=30, taps=taps)
            print("  boss flag at row", ckd.i - 1, "=", ckd.i - 1 - m_open, "after the opening", flush=True)
        except RuntimeError as ex:
            print("  FAILED:", ex, flush=True)
finally:
    eng.close()
