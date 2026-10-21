"""Does holding fire remove the lag frames of a segment? Replay rows, dropping B on rows a..b, and count lag frames.

    python tools/s5b_lagtest.py <state> <seg.json> <t_end> a-b [a-b ...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s1_common import Game  # noqa: E402

state, seg, t_end = sys.argv[1], sys.argv[2], int(sys.argv[3])
rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text())["rows"]]
g = Game(name="s5b_lagtest")
try:
    for spec in ["none"] + sys.argv[4:]:
        a, b = (10 ** 9, 0) if spec == "none" else [int(x) for x in spec.split("-")]
        g.load_file(state)
        lags, prev = [], None
        for i, row in enumerate(rows[:t_end]):
            if a <= i <= b:
                row = tuple(x for x in row if x != "B")
            r = g.step_raw(row)
            if prev is not None and r.fc == prev.fc and r.lr == 4:
                lags.append(i)
            prev = r
            if r.dead:
                break
        en = [(e[1], e[4], e[5]) for e in g.r.enemies()]
        print(spec, "lag", lags, "prog", g.r.prog, "dead", bool(g.r.dead), "nb", g.r.nbullets(), "enemies", len(en))
finally:
    g.close()
