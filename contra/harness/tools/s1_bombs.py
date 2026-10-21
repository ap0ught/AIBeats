"""Stage 1 boss: log the bomb turrets' bombs (trajectory per launch speed) from a hand-over state.

    python tools/s1_bombs.py <state> <variant 0..n>

The player runs right, drops to the ground and waits at the wall; variant k fires on a different schedule (the
bomb speed is RANDOM_NUM & 3 at launch, so the schedule changes the speeds seen).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s1  # noqa: E402
from contra.stages.s1_common import Game, log  # noqa: E402

state, var = sys.argv[1], int(sys.argv[2])
g = Game(name="s1_bombs")
try:
    g.load_file(state)
    tracks = {}
    auto_row = None
    for i in range(330):
        w = {"Right"}
        if var and (i // (3 + var)) % 2 == 0:
            w.add("B")
        r = g.step(w)
        if r.auto and auto_row is None:
            auto_row = i
        for e in r.enemies():
            if e[1] == 0x01:
                sl = e[0]
                m = r.m
                vx = m[0x508 + sl] + m[0x518 + sl] / 256.0
                vy = m[0x4E8 + sl] + m[0x4F8 + sl] / 256.0
                vx = vx - 256 if vx >= 128 else vx
                vy = vy - 256 if vy >= 128 else vy
                key = None
                for k_, tr in tracks.items():
                    if tr["slot"] == sl and tr["last"] == i - 1:
                        key = k_
                if key is None:
                    key = (i, sl)
                    tracks[key] = {"slot": sl, "start": i, "pts": [], "v0": (round(vx, 2), round(vy, 2)), "last": i}
                tracks[key]["pts"].append((e[4], e[5]))
                tracks[key]["last"] = i
        if r.dead:
            log("player died at row", i, r.x, r.y)
            break
    log(f"auto-scroll starts at row {auto_row}; player ends at x={g.r.x} y={g.r.y}")
    for key, tr in sorted(tracks.items()):
        p = tr["pts"]
        if p[0][1] not in (128,) or p[0][0] < 150:
            continue
        log(f"bomb at row {tr['start']} (auto+{tr['start'] - auto_row}) from {p[0]} v0 {tr['v0']} lives {len(p)} f; every 8th point: {p[::8]}")
finally:
    g.close()
