"""Where are the lag frames of stage 2 room 4, and what is on screen then? Replays a solved run's rows from the
stage start (emulator E[1]) and lists, for room 4: lag rows with the number of live player bullets, enemy slots in
use and sprites."""
import json
from contra.stages.base_common import BIT, make_fields, bullets, enemies
from contra.emulator import State

em = E[1]
em.set_fields(make_fields())
for tag, state in G.get("LAG", (("t3a", "s1/s2_start_legal_v2"), ("L2", "s1/s2_start_legal_v2"))):
    rep = json.load(open(f"logs/s2/{tag}_report.json"))
    rows = [tuple(r) for r in json.load(open(f"logs/s2/{tag}_rows.json"))]
    r4 = rep["rooms"][3]
    em.load(state)
    for r in rows[:r4["load"]]:
        em.cmd("stepx %02x" % sum(BIT[b] for b in r))
    T = 0
    out = []
    presses = []
    prevB = False
    hist = []
    for i, r in enumerate(rows[r4["load"]:r4["load"] + r4["frames"]]):
        s = State.parse(em.cmd("stepx %02x" % sum(BIT[b] for b in r)))
        nb = len(bullets(s))
        ne = len(enemies(s))
        if "B" in r and not prevB:
            presses.append(T + 1)
        prevB = "B" in r
        if s["lagged"]:
            out.append((i + 1, T, nb, ne))
        else:
            T += 1
            hist.append((T, nb, ne))
    print(tag, "room 4: load row", r4["load"], "frames", r4["frames"], "lag", r4["lag"], "last hit T", r4["last_hit_T"])
    print("   lag rows (row, T, bullets, enemies):", out)
    print("   presses at T:", presses)
    print("   bullets/enemies by T (every 8):", [(t, nb, ne) for t, nb, ne in hist if t % 8 == 0 and 120 <= t <= 300])
    print("   plan:", r4["plan"])
