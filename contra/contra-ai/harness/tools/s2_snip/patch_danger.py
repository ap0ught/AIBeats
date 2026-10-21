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


patch("contra/stages/base_plan.py", [
    ("              air=None, plated=(), jump_y=None):", "              air=None, plated=(), jump_y=None, danger=()):"),
    ('''                for (pose, hk), (mR, mL) in outcomes(t + FLIGHT, k, hps).items():
                    aR, aL = RF & mR, LF & mL
''', '''                bad = 0
                for (d0, d1, dm) in danger:      # places where standing up to shoot at this time was fatal
                    if d0 <= t <= d1:
                        bad |= dm
                for (pose, hk), (mR, mL) in outcomes(t + FLIGHT, k, hps).items():
                    aR, aL = RF & mR, LF & mL
                    if bad and pose == 0:
                        aR &= ~bad
                        aL &= ~bad
'''),
])
patch("contra/stages/base_room.py", [
    ('''            if s["death"] & 1:
                res["T"] = T
                return "death", res''', '''            if s["death"] & 1:
                res["T"] = T
                res["x"] = s["x"]
                return "death", res'''),
    ("        forbid = set()\n        noT = set()\n        nb4 = {}\n", "        forbid = set()\n        noT = set()\n        nb4 = {}\n        danger = []\n        deaths = set()\n"),
    ("not_before=nb4, air=air, plated=plated, jump_y=jump_y,", "not_before=nb4, air=air, plated=plated, jump_y=jump_y, danger=danger,"),
    ('''                elif st == "death":
                    lastp = max((p[0] for p in plan.presses if p[0] <= info["T"]), default=None)
                    if lastp is not None:
                        noT.add(lastp)''', '''                elif st == "death":
                    # standing there at that time was fatal: keep Bill away from that spot around that time;
                    # if the same death comes back, also give up the press before it
                    danger.append((info["T"] - 8, info["T"] + 1, bp.mask_range(info["x"] - 7, info["x"] + 7)))
                    key = (info["T"], info["x"] // 4)
                    lastp = max((p[0] for p in plan.presses if p[0] <= info["T"]), default=None)
                    if key in deaths and lastp is not None:
                        noT.add(lastp)
                    deaths.add(key)'''),
    ("    def __init__(self, S: Sess, verbose=True, beam=12000, ntop=6, max_replans=12):",
     "    def __init__(self, S: Sess, verbose=True, beam=12000, ntop=6, max_replans=20):"),
])
print("patched")
