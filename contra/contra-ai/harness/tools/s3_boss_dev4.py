"""Development: hill climbing on the dragon fight schedule from a saved state 70 rows before the mouth opens.
    python tools/s3_boss_dev4.py <climb name> [x=123] [iters=400]"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Pad, LOGS_DIR  # noqa: E402
from contra.stages.s3s8_engine import Engine, Ck, gen, new_ov  # noqa: E402
from contra.stages import s3_boss  # noqa: E402
from contra.stages.s8 import climb, fail_index, log  # noqa: E402

name = sys.argv[1]
xt = int(sys.argv[2]) if len(sys.argv) > 2 else 123
iters = int(sys.argv[3]) if len(sys.argv) > 3 else 400
j = json.loads((LOGS_DIR / f"{name}_m70.rows.json").read_text())
rows = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
M = j["m_open"]
eng = Engine(3, tag=name.replace("/", "_"))
try:
    ck0 = Ck(f"{name}_m70", len(rows), rows, Pad.from_rows(rows))
    x0 = eng.sim(ck0, [()])[0]["x"]
    ov = new_ov()
    dx = xt - 2 - x0                       # walk to xt - 2, then a 2-frame tap right to face right
    ov["holds"].append((ck0.i, ck0.i + abs(dx), "Right" if dx > 0 else "Left"))
    ov["holds"].append((ck0.i + abs(dx) + 2, ck0.i + abs(dx) + 4, "Right"))
    a0 = ck0.i + abs(dx) + 6
    ov["aims"].append((a0, M + 400, "Up"))
    ov["nofire"].append((ck0.i, M - 40))
    ov["jumps"] += [M - 12, M + 48]
    ov["holds"].append((M + 49, M + 51, "Left"))
    ov["holds"].append((M + 60, M + 62, "Right"))
    N = 70 + 260

    def cost(t):
        fi, _k = fail_index(t, 0x13, stall_ok=lambda s: True)
        for k, s in enumerate(t):
            if fi is not None and k >= fi:
                return 10 ** 6 - fi
            if s["bossdef"]:
                return k
        return 10 ** 4 + (s3_boss.mouth_hp(t[-1]) or 99) * 10

    lo, hi = M - 30, M + 130

    def mut(o, rng):
        o = {k: list(v) for k, v in o.items()}
        r = rng.random()
        if r < 0.3 and o["jumps"]:
            jx = rng.choice(o["jumps"])
            o["jumps"].remove(jx)
            o["jumps"].append(jx + rng.choice((-6, -4, -2, -1, 1, 2, 4, 6)))
        elif r < 0.36:
            o["jumps"].append(rng.randrange(lo, hi))
        elif r < 0.4 and len(o["jumps"]) > 1:
            o["jumps"].remove(rng.choice(o["jumps"]))
        elif r < 0.7:
            hs = [h for h in o["holds"] if h[0] >= lo]
            if hs:
                h = rng.choice(hs)
                o["holds"].remove(h)
                d = rng.choice((-6, -4, -2, -1, 1, 2, 4, 6))
                o["holds"].append((h[0] + d, h[1] + d + rng.choice((0, 0, 1, 2)), h[2]))
        elif r < 0.82:
            a = rng.randrange(lo, hi)
            k = rng.choice((6, 8, 10, 12, 16))
            d1 = rng.choice(("Left", "Right"))
            o["holds"].append((a, a + 2, d1))
            o["holds"].append((a + k, a + k + 2, "Right" if d1 == "Left" else "Left"))
        elif r < 0.9:
            hs = [h for h in o["holds"] if h[0] >= lo]
            if hs:
                o["holds"].remove(rng.choice(hs))
        else:
            a = rng.randrange(M - 40, hi)
            o["nofire"].append((a, a + rng.choice((1, 2, 3))))
        return o

    ovb, c, t = climb(eng, ck0, ov, N, cost, mut, iters, f"B-climb-x{xt}", base=(), patience=iters)
    print("best cost", c, "=> boss flag", c - 70, "rows after the opening" if c < 10 ** 4 else "")
    print(ovb)
    hp = [(k - 70, s3_boss.mouth_hp(s)) for k, s in enumerate(t) if k % 10 == 0 and k >= 60]
    print(hp[:30])
    print("lag frames in the fight:", sum(1 for s in t[70:c if c < 10 ** 4 else len(t)] if s["lagged"]))
    (LOGS_DIR / f"{name}_fight_x{xt}.json").write_text(json.dumps({"ov": ovb, "cost": c}))
finally:
    eng.close()
