"""Trace a stage 1 boss fight: python tools/s1b_trace.py <boss state> <rows.json (all rows)> <run rows>"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s1  # noqa: E402
from contra.stages.s1_common import Game  # noqa: E402

state, nrun = sys.argv[1], int(sys.argv[3])
rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(sys.argv[2]).read_text())]
g = Game(name="s1b_trace")
try:
    g.load_file(state)
    a0 = None
    for i, row in enumerate(rows[nrun:]):
        r = g.step_raw(row)
        if r.auto and a0 is None:
            a0 = i
        d = s1.door(r)
        bombs = [(e[4], e[5]) for e in r.enemies() if e[1] == 1 and (r.m[0x588 + e[0]] & 15) == 5]
        oth = [(e[1], e[4], e[5], e[3]) for e in r.enemies() if e[1] not in (1, 0x11)]
        print(f"i={i:3d} a={'' if a0 is None else i - a0:>3} scr={r.scr} x={r.x:3d} wx={r.prog} y={r.y:3d} air={1 if r.air else 0} aim={r.aim} hp={s1.door_hp(r):2d} "
              f"door={(d[4], d[5]) if d else None} {'+'.join(row):14s} nb={r.nbullets()} "
              f"B={[(b[1], b[2], b[3]) for b in r.bullets()]} bombs={bombs} en={oth}")
finally:
    g.close()
