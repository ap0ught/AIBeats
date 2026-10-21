"""Dump a stage's background collision map (16x16 px cells) by replaying a segment and reading BG_COLLISION_DATA.

    python tools/s1_map.py <state> <seg.json|inputs.txt> <out.txt> [max_frames]

Characters: '.' empty, '=' floor (one-way), '~' water, '#' solid. First value seen for a cell is kept
(bridges that explode later are shown intact). Column header = screen number / 16-px column in the screen.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.inputs import read_inputs  # noqa: E402
from contra.stages.s1_common import Game  # noqa: E402

state, seg, out = sys.argv[1], sys.argv[2], sys.argv[3]
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 100000
if seg.endswith(".json"):
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text())["rows"]]
else:
    rows = read_inputs(seg)
rows = rows[:mx]
cells = {}
g = Game(name="s1_map")
try:
    g.load_file(state)
    lvl = None
    for row in rows:
        r = g.step_raw(row)
        if r.lr not in (4, 8, 9):
            continue
        if lvl is None:
            lvl = r.level
        if r.level != lvl:
            break
        base = r.scr
        off = (-base) % 16
        for x in range(off, 256, 16):
            wc = (base + x) // 16
            for row_ in range(14):
                key = (wc, row_)
                if key not in cells:
                    cells[key] = r.coll(min(x + 8, 255), row_ * 16 + 8)
finally:
    g.close()
maxc = max(k[0] for k in cells)
ch = ".=~#"
lines = []
lines.append("     " + "".join(f"{(c // 16) % 100:<16d}" if c % 16 == 0 else "" for c in range(maxc + 1)))
lines.append("     " + "".join("0123456789abcdef"[c % 16] for c in range(maxc + 1)))
for row_ in range(14):
    lines.append(f"y{row_ * 16:3d} " + "".join(ch[cells.get((c, row_), 0)] for c in range(maxc + 1)))
Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
