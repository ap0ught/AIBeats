"""NesHawk port of up17: lives / health / score when each level ends, reference capture against port capture.

    python u17p_levels.py <reference capture tag> <port capture tag>        e.g. u17p_levels.py u17q u17v2

Both captures are `core_check_toads.py run` captures (2 KB of RAM per frame). For every change of the level byte $10 away
from a level (not from a 254 / 255 page) prints, for both runs: the frame, lives $11, health $51A and the score digits
$5F4-$5F9 on the last frame of the level, and says whether the port's row equals the reference's. Also the landing frame
($3B5 5 -> 4 in Level 1), both 13 -> 254 cuts and the run time (second cut - landing) / 60.0988. Reads only.
"""
import json
import sys
from pathlib import Path

import numpy as np

FIX = Path(__file__).resolve().parent / "logs" / "fix"
NTSC = 60.0988
NAMES = {1: "Level 1", 3: "Turbo Tunnel", 4: "Arctic Caverns", 8: "Karnath's Lair", 7: "Intruder Excluder", 11: "Terra Tubes",
         9: "Rat Race", 10: "Clinger-Winger", 5: "The Revolution", 13: "Dark Queen"}


def events(tag):
    R = np.memmap(FIX / f"core_{tag}.ram", dtype=np.uint8, mode="r").reshape(-1, 0x800)
    summ = json.loads((FIX / f"core_{tag}.json").read_text())
    lv = R[:, 0x10].astype(int)
    anim = R[:, 0x3B5].astype(int)
    n = len(R) - 1
    landing = next((f for f in range(1, n + 1) if lv[f] == 1 and anim[f - 1] == 5 and anim[f] == 4), None)
    rows = []
    for f in range(1, n + 1):
        if lv[f] != lv[f - 1] and lv[f - 1] in NAMES:
            m = R[f - 1]
            score = "".join(str(int(x) & 15) for x in m[0x5F4:0x5FA])
            rows.append((int(lv[f - 1]), int(lv[f]), f, int(m[0x11]), int(m[0x51A]), score))
    cuts = [f for f in range(1, n + 1) if lv[f - 1] == 13 and lv[f] == 254]
    lives = [(f, int(R[f - 1, 0x11]), int(R[f, 0x11])) for f in range(1, n + 1) if R[f, 0x11] != R[f - 1, 0x11] and lv[f] in NAMES]
    return summ, landing, rows, cuts, lives, n


a, b = sys.argv[1], sys.argv[2]
sa, la, ra, ca, liva, na = events(a)
sb, lb, rb, cb, livb, nb = events(b)
print(f"{a}: {sa['core_info']['core_seen']} {sa['inputs']} {na} frames | {b}: {sb['core_info']['core_seen']} {sb['inputs']} {nb} frames")
print(f"landing: {a} {la}  {b} {lb}")
ok = len(ra) == len(rb)
print(f"{'level':<18} {'ends ->':>8} | {a + ' frame':>12} lives hp  score  | {b + ' frame':>12} lives hp  score  | frames | same lives/health/score")
for i in range(max(len(ra), len(rb))):
    x = ra[i] if i < len(ra) else None
    y = rb[i] if i < len(rb) else None
    same = x is not None and y is not None and x[0] == y[0] and x[1] == y[1] and x[3:] == y[3:]
    ok = ok and same
    fx = f"{x[2]:>12} {x[3]:>5} {x[4]:>2} {x[5]}" if x else " " * 28
    fy = f"{y[2]:>12} {y[3]:>5} {y[4]:>2} {y[5]}" if y else " " * 28
    nm = NAMES.get((x or y)[0], "?")
    to = (x or y)[1]
    print(f"{nm:<18} {to:>8} | {fx} | {fy} | {(y[2] - x[2]) if x and y else '':>+6} | {'yes' if same else 'NO'}")
print(f"lives changes inside levels (frame, from, to): {a} {liva}")
print(f"                                               {b} {livb}")
same_lives = [(p, q) for _, p, q in liva] == [(p, q) for _, p, q in livb]
print(f"13 -> 254 cuts: {a} {ca}  {b} {cb}")
for tag, land, cuts in ((a, la, ca), (b, lb, cb)):
    if land and len(cuts) > 1:
        t = cuts[1] - land
        s = t / NTSC
        print(f"RUN TIME {tag}: T. Bird cut {cuts[1]} - landing {land} = {t} frames = {s:.3f} s = {int(s // 60)}:{s % 60:05.2f}; "
              f"under 12:00.00 (720.00 s): {s < 720.0}")
print("VERDICT:", "LIVES / HEALTH / SCORE AT EVERY LEVEL END EQUAL THE REFERENCE'S, same sequence of lives changes"
      if ok and same_lives else "DIFFERENT")
