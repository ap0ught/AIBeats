"""Development driver for the boss beam (stage 8): python tools/s8_beam_dev.py guardian|heart [W] [state] [row]"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, Ck, hpos, find_slot  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR, Pad, check_rows  # noqa: E402
from contra.stages.s3s8_fight import FightCfg, beam_fight  # noqa: E402

which = sys.argv[1]
W = int(sys.argv[2]) if len(sys.argv) > 2 else 12
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / "s8/best.seg.json").read_text())["rows"]]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


if which == "guardian":
    state, i0 = (sys.argv[3], int(sys.argv[4])) if len(sys.argv) > 4 else ("s8/dev_g437", 437)
    cfg = FightCfg(typ=0x10, box=(-27, 28, -17, 18), virt=(432, 240, 96, 496), W=W, name="guardian", log=log,
                   strat_until=517 + 75,
                   jump_mode=lambda s, js: "free" if (not js and hpos(s) < 560) else "asap")
else:
    state, i0 = (sys.argv[3], int(sys.argv[4])) if len(sys.argv) > 4 else ("s8/dev_h2749", 2749)
    cfg = FightCfg(typ=0x16, box=(-27, 28, -27, 28), virt=(2512, 240, 112, 2560), W=W, name="heart", log=log,
                   strat_until=2829 + 130,
                   jump_mode=lambda s, js: "asap" if (js or s["autodone"]) else "free")
with Engine(3, tag="s8") as eng:
    ck = Ck(state, i0, rows[:i0], Pad.from_rows(rows[:i0]))
    out, info = beam_fight(eng, ck, cfg)
    print(info)
    allrows = rows[:i0] + out
    print("violations", check_rows(allrows))
    (LOGS_DIR / f"s8/p2/beam_{which}_W{W}.json").write_text(json.dumps({"i0": i0, "rows": ["+".join(r) for r in out], "info": info}))
