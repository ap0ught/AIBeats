"""Show the Eye phase of a solved stage 2 run: python tools/s2t_eyeshow.py <tag>
(per boss row from the platings' end: buttons, and the HP events recorded by the fight)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tag = sys.argv[1]
rep = json.loads((ROOT / "logs" / "s2" / f"{tag}_report.json").read_text())
rows = json.loads((ROOT / "logs" / "s2" / f"{tag}_rows.json").read_text())
b0 = rep["boss_load"]
boss = rep["boss"]
pd = boss.get("plates_done")
ev = {r: hp for r, hp in boss["events"]}
print("boss load row", b0, "platings done boss row", pd, "frames", boss["frames"], "drops", boss.get("drops"))
line = []
for r in range(pd - 30, boss["frames"] + 1):
    row = rows[b0 + r - 1]
    s = "".join({"Left": "L", "Right": "R", "Up": "U", "A": "A", "B": "B", "Down": "D"}.get(b, "?") for b in row) or "."
    e = ev.get(r)
    line.append(f"{r}:{s}" + (f"[{e[1]}]" if e else ""))
print(" ".join(line))
