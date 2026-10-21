"""One-off patch of yt/run_text.py for the 11:54 route (2026-10-10): the tower with one lap of the level clock gained
(T12a/T12x), the boss fight's length read from the trace, TOWER1's tokens. Keeps yt/run_text.py.backup_1154."""
import os
import shutil
from pathlib import Path

p = Path(__file__).resolve().parent / "run_text.py"
s = p.read_text(encoding="utf-8")
if not (p.parent / "run_text.py.backup_1154").exists():
    shutil.copy(p, p.parent / "run_text.py.backup_1154")


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


# --- the frame Robo-Manus is gone (his object leaves the table) = the kill
rep('''        if robo is None and lv == 7 and any(kv.get(f"id{s}") == 0x7D for s in range(2, 8)):
            robo = k
''', '''        here = lv == 7 and any(kv.get(f"id{s}") == 0x7D for s in range(2, 8))
        if robo is None and here:
            robo = k
        if robo is not None and robo_dead is None and lv == 7 and not here and k > robo + 200:
            robo_dead = k
''')
rep("    last_hit = robo = None\n", "    last_hit = robo = robo_dead = None\n")
rep("             robo=robo, total=rows[-1][0])", "             robo=robo, robo_dead=robo_dead, total=rows[-1][0])")

# --- variants
rep('''    karnath_new = lens[segs[4]] < 2540                     # K6 / C6: the record's line in the warp room
''', '''    karnath_new = lens[segs[4]] < 2540                     # K6 / C6 / K7: the record's line in the warp room
    lap = lens[segs[9]] < 8300                             # T12a / T12x: one lap of the level clock gained in the tower
    sh = 258 if lap else 0                                 # the tower's second half comes this many frames sooner
    fight = (F["robo_dead"] - (s8 + 2753)) if F.get("robo_dead") else 652   # control is 2,753 inputs into the segment
''')
rep('''||21 smashes and the kill in 652 frames. The published run chased him for 1,087"),''',
    '''||21 smashes and the kill in " + str(fight) + " frames. The published run chased him for 1,087"),''')

# --- the tower: the first half
a = s.index('''        (L12 + 1260, 'KILL the Hornhead - 3 hits.''')
b = s.index('''        (s12 + 5200, "THE TAS'S KILL''')
old_first = s[a:b]
new_first = '''    ]
    if lap:
        ev += [
            (s12 + 880, "THE SPRING STAIRCASE on the reference run's line: a fresh press of A the frame the toad lands on each spring. Its banned Left+Right frames are swapped for legal taps.||333 frames ahead of the published run by the next Hornhead"),
            (s12 + 1545, "A GROUND KICK, then the big boot. A flying kick lands sooner - but it scores 250 points more, and the Dark Queen's fight only replays if the score is exactly what it was.||Kick 750, flying kick 1,000, big boot 5,000"),
            (s12 + 1700, "The legal dash to the spring - tap, let go, hold - is 6 to 8 frames slower than the reference run's Left+Right. Still 357 frames ahead once the walker is dead.||"),
            (s12 + 2300, "STANDING STILL ON PURPOSE. The green ledges above are solid for only part of a 256-frame cycle of the level's clock. 344 frames early is the wrong moment, so the toad gives 88 back and arrives exactly one lap early.||Any other gain would shift the timing of every fight and jump behind it"),
            (s12 + 3065, 'A boss cloud that only comes down when the random number generator says so.||Every button press changes the generator'),
        ]
    else:
        ev += [
''' + old_first.replace("        (L12 +", "            (L12 +") + '''        ]
    ev += [
'''
s = s[:a] + new_first + s[b:]
for i, extra in ((5200, None), (5340, None), (5440, None)):
    rep(f"        (s12 + {i}, ", f"        (s12 + {i} - sh, ")
rep('''        (s12 + 5950, "The lift and the platforms above appear with the camera, not with the clock: every frame gained below carries straight up the tower.||129 frames ahead of the published run at this platform"),''',
    '''        (s12 + 5950 - sh, "The lift and the platforms above appear with the camera, not with the clock: every frame gained below carries straight up the tower.||" + str(129 + sh) + " frames ahead of the published run at this platform"),''')
rep('''        (s12 + 6270, "THE WALKER IS ONE JUGGLE, not five fights: a running kick, a second kick, two dash-jump air kicks while it hangs stunned - then a ram at sprint speed that kills it and carries the toad onto the spring.||Dead 209 frames sooner than in the published run"),''',
    '''        (s12 + 6270 - sh, "THE WALKER IS ONE JUGGLE, not five fights: a running kick, a second kick, two dash-jump air kicks while it hangs stunned - then a ram at sprint speed that kills it and carries the toad onto the spring.||Dead " + str(209 + sh) + " frames sooner than in the published run"),''')
rep('''        (s12 + 6546, "WIND FACE 3, 408 frames sooner. The lower spring passes under its pole just as the wind stops: drop, pump, up.||A pole cannot be let go of while the wind blows"),''',
    '''        (s12 + 6546 - sh, "WIND FACE 3, " + str(408 + sh) + " frames sooner. The lower spring passes under its pole just as the wind stops: drop, pump, up.||A pole cannot be let go of while the wind blows"),''')
rep('''        (s12 + 7123, "WIND FACE 4, 422 frames sooner.||The reference run scrolls the camera faster here with Left+Right; legally it climbs 1 px a frame"),''',
    '''        (s12 + 7123 - sh, "WIND FACE 4, " + str(422 + sh) + " frames sooner.||The reference run scrolls the camera faster here with Left+Right; legally it climbs 1 px a frame"),''')
rep('''        (s12 + 7640, "THE TOP: sprint the last floor, a dash jump, a shorter last hop - then hold A on the top ledge until the camera arrives.||469 frames faster than the published tower"),''',
    '''        (s12 + 7640 - sh, "THE TOP: sprint the last floor, a dash jump, a shorter last hop - then hold A on the top ledge until the camera arrives.||" + str(8880 - lens[segs[9]]) + " frames faster than the published tower"),''')

# --- tokens: TOWER1 counts when its tower is in the route; the up17 workflow counts for this route
rep('''    use17 = name.startswith("run17") or "up17" in name
''', '''    use17 = lap or karnath_new
''')
rep('''        if r["part"] == "tower1" or (r["part"] == "karnath" and not karnath_new) or (r["name"].startswith("wf_3c1656de") and not use17):
            continue
        a = part.setdefault(r["part"], [0, 0.0])''', '''        if (r["part"] == "tower1" and not lap) or (r["part"] == "karnath" and not karnath_new) or (r["name"].startswith("wf_3c1656de") and not use17):
            continue
        a = part.setdefault("tower" if r["part"] == "tower1" else r["part"], [0, 0.0])''')
rep('''            "The Revolution done": "The top of the tower without the banned camera trick. Recovery: the tower's second half rebuilt from "
                                   "the reference run's line with legal sprints - 7.8 seconds.",''',
    '''            "The Revolution done": ("The top of the tower without the banned camera trick. Recovery: the tower rebuilt from the reference "
                                    "run's line with legal sprints, and one whole lap of the level's clock gained - 12 seconds.") if lap else
                                   ("The top of the tower without the banned camera trick. Recovery: the tower's second half rebuilt from "
                                    "the reference run's line with legal sprints - 7.8 seconds."),''')
rep('''             ("Clinger-Winger done", L12), ("Revolution: the camera locks", L12 + 1810), ("Revolution: three wind faces", L13 - 430),''',
    '''             ("Clinger-Winger done", L12), ("Revolution: the camera locks", L12 + 1810 - (130 if lap else 0)), ("Revolution: three wind faces", L13 - 430),''')
tmp = p.with_suffix(".py.tmp")
tmp.write_text(s, encoding="utf-8", newline="\n")
import ast
ast.parse(s)
os.replace(tmp, p)
print("patched", p)
