"""Replay a stage segment and print every frame on which forward progress (scroll + auto-scroll credit) is lost.

    python tools/s5b_loss.py <stage 1|5> <state> <seg.json> [max_rows]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s1_common import Game  # noqa: E402

stage, state, seg = int(sys.argv[1]), sys.argv[2], sys.argv[3]
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 6
rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text())["rows"]][:mx]
g = Game(name=f"s{stage}b_loss")
try:
    g.load_file(state)
    prev = None
    loss = 0
    out = []
    for i, row in enumerate(rows):
        r = g.step_raw(row)
        if r.lr != 4 or r.auto or r.bossdef:
            prev = r
            if r.auto or r.bossdef:
                break
            continue
        if prev is not None and prev.lr == 4:
            dp = r.prog - prev.prog
            lag = r.fc == prev.fc
            ts = r.tank_scroll if stage == 5 else 0
            exp = 1 + (1 if (ts and (r.fc & 1)) else 0)
            if dp < 1:
                loss += 1 - dp
                why = "LAG" if lag else ("A" if "A" in row and not prev.air else ("land" if prev.air and not r.air else ("air" if r.air else "gnd")))
                out.append(f"t={i:5d} prog={r.prog:5d} x={r.x:3d} y={r.y:3d} d={dp:+d} loss={loss:3d} {why:5s} in={'+'.join(row)}")
        prev = r
    print("\n".join(out))
    print("total loss", loss, "rows", len(rows))
finally:
    g.close()
