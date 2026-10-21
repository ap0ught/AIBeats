"""Rows without forward progress in a finished stage 8 segment (read-only replay).
    python tools/s8_noprogress.py <state> <seg.json> [from] [to]"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, hpos  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR  # noqa: E402

state, seg = sys.argv[1], sys.argv[2]
a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
b = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 6
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / seg).read_text())["rows"]]
with Engine(1, tag="s8") as eng:
    tr = eng.sim(eng.root(state), rows)
    out = []
    for i in range(max(1, a), min(b, len(tr))):
        if hpos(tr[i]) <= hpos(tr[i - 1]):
            s = tr[i]
            why = "LAG" if s["lagged"] else ("A" if "A" in rows[i] and (i == 0 or "A" not in rows[i - 1]) else
                                             ("land" if (tr[i - 1]["jump"] or tr[i - 1]["edge"]) and not (s["jump"] or s["edge"]) else "?"))
            out.append((i, hpos(s), s["x"], s["y"], why, "+".join(rows[i])))
    runs = []
    for o in out:
        if runs and o[0] == runs[-1][-1][0] + 1:
            runs[-1].append(o)
        else:
            runs.append([o])
    for r in runs:
        print(f"rows {r[0][0]}..{r[-1][0]} ({len(r)}): pos {r[0][1]} x{r[0][2]} y{r[0][3]} {[o[4] for o in r][:6]} {r[0][5]}")
    print("total rows without progress:", len(out))
