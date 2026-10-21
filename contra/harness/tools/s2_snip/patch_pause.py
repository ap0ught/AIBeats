import os

ROOT = ""


def patch(path, reps):
    p = ROOT + path
    s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)


patch("contra/stages/s2.py", [
    ("def solve(emu, state, hist=(), verbose=True, beam=12000, save_states=None, boss_width=12, boss=None, rooms_only=False,\n          boss_hold=4):",
     "def solve(emu, state, hist=(), verbose=True, beam=12000, save_states=None, boss_width=12, boss=None, rooms_only=False,\n          boss_hold=4, pause=0):"),
    ("    S.step(())                       # the room's enemies appear on the next frame: T = 0\n",
     '''    if pause:
        # a different start condition for testing: pause for `pause` frames before the first room's logic starts
        # (shifts the frame counter and the random number relative to everything in the stage; costs its length)
        S.step(("Start",))
        S.step(("Start",))
        for _ in range(max(2, pause - 2)):
            S.step(())
        S.step(("Start",))               # logic resumes on this frame: T = 0
        out["pause_rows"] = len(S.rows) - 1
    else:
        S.step(())                       # the room's enemies appear on the next frame: T = 0
'''),
])
patch("contra/stages/s4.py", [
    ("def solve(emu, state, hist=(), verbose=True, beam=12000, save_states=None, boss_width=12, rooms_only=False,\n          boss_hold=4):",
     "def solve(emu, state, hist=(), verbose=True, beam=12000, save_states=None, boss_width=12, rooms_only=False,\n          boss_hold=4, pause=0):"),
    ("boss_width=boss_width, boss=BOSS, rooms_only=rooms_only, boss_hold=boss_hold)",
     "boss_width=boss_width, boss=BOSS, rooms_only=rooms_only, boss_hold=boss_hold, pause=pause)"),
])
print("patched")
