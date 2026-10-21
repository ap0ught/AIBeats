"""Development: polish a beam result. python tools/s8_polish_dev.py guardian|heart <beam json> [iters] [emus]"""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, Ck, find_slot  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR, Pad, check_rows  # noqa: E402
from contra.stages.s3s8_fight import polish_rows  # noqa: E402

which, bj = sys.argv[1], sys.argv[2]
iters = int(sys.argv[3]) if len(sys.argv) > 3 else 200
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / "s8/best.seg.json").read_text())["rows"]]
b = json.loads((LOGS_DIR / bj).read_text())
i0 = b["i0"]
brow = [tuple(x for x in r.split("+") if x) for r in b["rows"]]
typ = 0x10 if which == "guardian" else 0x16
state = "s8/dev_g437" if which == "guardian" else "s8/dev_h2749"


def kill(s):
    k = find_slot(s, typ)
    return k is not None and s[f"h{k}"] == 0


with Engine(int(sys.argv[4]) if len(sys.argv) > 4 else 3, tag="s8") as eng:
    ck = Ck(state, i0, rows[:i0], Pad.from_rows(rows[:i0]))
    t0 = time.time()
    out, best = polish_rows(eng, ck, brow, kill, iters=iters, log=lambda *a: print(time.strftime("%H:%M:%S"), *a, flush=True),
                            lo=40)
    print(f"kill index {len(brow) - 1} -> {best} ({time.time() - t0:.0f}s); violations", check_rows(rows[:i0] + out))
