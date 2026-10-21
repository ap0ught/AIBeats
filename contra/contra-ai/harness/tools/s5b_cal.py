"""Calibration dump for the offline UFO model: every frame of a scripted UFO fight, Bill's Y state and the raw
bullet RAM (slot, routine, x, xacc, y, yacc, vx16, vy16, timer)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s5  # noqa: E402
from contra.stages.s1_common import Game  # noqa: E402

state = sys.argv[1]
job = [int(x) for x in sys.argv[2:]]
g = Game(name="s5b_cal")
try:
    g.load_file(state)
    n = s5.ufo_script3(g, 102, *job)
    rows = list(g.rows)
    g.load_file(state)
    for i, row in enumerate(rows):
        r = g.step_raw(row)
        m = r.m
        e = s5.ufo(r)
        bl = []
        for s in range(10):
            if m[0x388 + s]:
                vx = m[0x408 + s] * 256 + m[0x3E8 + s]
                vy = m[0x3F8 + s] * 256 + m[0x3D8 + s]
                vx -= 65536 if vx >= 32768 else 0
                vy -= 65536 if vy >= 32768 else 0
                bl.append((s, m[0x438 + s], m[0x3C8 + s], m[0x3A8 + s], m[0x3B8 + s], m[0x398 + s], vx, vy, m[0x418 + s], m[0x4A8 + s]))
        if i >= 60:
            print(f"k={i + 1} fc={r.fc} y={r.y} sub={m[0x94]} vy={(m[0xC6] * 256 + m[0xC4])} jmp={m[0xA0]} x={r.x} aim={r.aim} hp={e[3] if e else -1} st={e[6] if e else -1} "
                  f"row={'+'.join(row)} lagged={r.lagged} B={bl} E={[(x[0], x[1], x[4], x[5], x[3], x[6]) for x in r.enemies() if x[1] != 0x14]}")
finally:
    g.close()
