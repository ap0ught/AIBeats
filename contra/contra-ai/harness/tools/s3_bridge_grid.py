"""Bridge experiment (read-only replay of a finished run's rows with two waits changed):
    python tools/s3_bridge_grid.py <state> <seg.json> <row -34 standing> <jump row> <bridge landing row> <skip A row> <skip end row>

v3: standing on row -34 at 721, the jump to the bridge starts at row J1 (after a wait), lands at row B, Bill walks
right until the skip jump's A at row J2 and stands on row -41 at row E. Grid: wait w on row -34 (instead of
J1 - 721) and walk k on the bridge (instead of J2 - B); the two jumps' own rows are reused unchanged.
Prints, per (w, k): the row Bill stands on row -41, or what went wrong.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, Ck  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR, Pad, check_rows  # noqa: E402

state, seg = sys.argv[1], sys.argv[2]
S, J1, B, J2, E = (int(x) for x in sys.argv[3:8])
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / seg).read_text())["rows"]]
jump1 = rows[J1:B]          # the jump onto the bridge
jump2 = rows[J2:E + 1]      # the skip jump
with Engine(1, tag="s3") as eng:
    root = eng.root(state)
    ck, _ = eng.commit(root, rows[:S], keep="s3/p2_bridge_s")
    res = {}
    for w in range(int(sys.argv[8]) if len(sys.argv) > 8 else 40, J1 - S + 2, 2):
        line = []
        for k in range(24, J2 - B + 2, 3):
            cand = [()] * w + jump1 + [("Right",)] * k + jump2 + [()] * 10
            tr = eng.sim(ck, cand)
            died = next((i for i, s in enumerate(tr) if s["death"] & 1 or s["pstate"] != 1), None)
            a = tr[-1]["screen"] * 240 + tr[-1]["scroll"]
            q = (tr[-1]["y"] + 16 - a) >> 4
            land = next((i for i in range(w + len(jump1) + k + 5, len(tr)) if not tr[i]["jump"] and not tr[i]["edge"]), None)
            if died is not None:
                line.append(f"k{k}:dead@{died}")
            elif q == -41 and land is not None:
                line.append(f"k{k}:OK@{S + land}")
                res[(w, k)] = S + land
            else:
                line.append(f"k{k}:q{q}")
        print(f"w={w:3d} " + " ".join(line), flush=True)
    if res:
        b = min(res.items(), key=lambda z: z[1])
        print("best", b)
