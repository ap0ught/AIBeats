"""u17v_plan.py - builds the screenshot / branch plans for u17v_replay.py from logs/fix/u17v_run1_analysis.json."""
import json
from pathlib import Path

FIX = Path(__file__).resolve().parent / "logs" / "fix"
an = json.loads((FIX / "u17v_run1_analysis.json").read_text())
ch = an["level_changes"]
land = an["landing"]
cut1, cut2 = an["cuts_13_254"][:2]
N = an["frames"]
shots = {}


def add(f, name):
    if 1 <= f <= N:
        shots.setdefault(f, name)


# landing, every frame
for f in range(land - 14, land + 14):
    add(f, f"land_f{f:05d}")
levels = [r for r in an["levels"]]
EVERY = {8: 40, 7: 45, 5: 90}              # the parts that are new against up16b2: Karnath, Level 8, the tower
for r in levels:
    b, a, z = r["byte"], r["first"], r["last"]
    step = EVERY.get(b, 150)
    for f in range(a + 30, z + 1, step):
        add(f, f"play_b{b:02d}_f{f:05d}")
    for f in range(z - 240, z + 1, 20):       # the last 240 frames of each level
        add(f, f"exit_b{b:02d}_f{f:05d}")
    for f in range(a, a + 121, 15):           # the first 120 frames
        add(f, f"entry_b{b:02d}_f{f:05d}")
# deaths: Turbo Tunnel skip, Terra Tubes spikes (health -> 0 outside a load)
for f, a, b, l in an["health_drops"]:
    if b == 0 and a == 47 and l in (3, 11) and not any(abs(f - c[0]) < 60 for c in ch):
        for g in range(f - 60, f + 140, 10):
            add(g, f"death_b{l:02d}_f{g:05d}")
# lives changes
for f, a, b in an["lives_changes"]:
    if f > 1413:
        for g in (f - 1, f, f + 30):
            add(g, f"lives_f{g:05d}")
# cuts as the route plays them
for f in range(cut1 - 4, cut1 + 41):
    add(f, f"cut1route_f{f:05d}")
for f in range(cut2 - 12, cut2 + 1):
    add(f, f"cut2_f{f:05d}")
(FIX / "u17v_plan_run2.json").write_text(json.dumps({"shots": shots, "post": 90}))
print("run2:", len(shots), "pictures + 90 after the list")

# run3: the game's own pages with nothing pressed, and the first cut with nothing pressed
br = []
for i, (f, a, b) in enumerate(ch):
    if f < 1413 or f >= cut1:
        continue
    if b == 254 or (a == 255 and b not in (254, 255)) or (a == 5 and b == 13):
        br.append({"frame": f, "n": 150, "every": 10, "name": f"page_f{f:05d}_{a}to{b}"})
br.append({"frame": cut1, "n": 480, "every": 2, "name": f"cut1noinput_f{cut1:05d}"})
(FIX / "u17v_plan_run3.json").write_text(json.dumps({"branches": br}))
print("run3:", len(br), "branches")
