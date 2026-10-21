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
    ("              air=None, plated=(), jump_y=None, danger=()):",
     "              air=None, plated=(), jump_y=None, danger=(), kill_by=None):"),
    ('''        for (cd, slots, hps, jp), (R, back) in states.items():
            if t + FLIGHT >= best_fin:
                continue
''', '''        for (cd, slots, hps, jp), (R, back) in states.items():
            if t + FLIGHT >= best_fin:
                continue
            if kill_by and any(hps[eid] > 0 and t > tk for eid, tk in kill_by.items()):
                continue                    # a soldier that had to be shot by now (its bullets killed Bill) is alive
'''),
])
patch("contra/stages/base_room.py", [
    ("        danger = []\n        deaths = set()\n", "        danger = []\n        deaths = set()\n        kill_by = {}\n"),
    ("jump_y=jump_y, danger=danger,", "jump_y=jump_y, danger=danger, kill_by=kill_by,"),
    ('''            if not plans and long and t_max < long[1]:''', '''            if not plans and kill_by:
                kill_by = {}                # the "shoot the soldiers early" demand cannot be met: drop it
                continue
            if not plans and long and t_max < long[1]:'''),
    ('''                    deaths.add(key)''', '''                    deaths.add(key)
                    if not kill_by and len(deaths) == 1:
                        # first death in this room: demand that every soldier on the wall by then is shot within
                        # 45 frames of appearing (their bullets come straight down where Bill has to stand)
                        kill_by = {e.eid: e.open + 45 for e in ents
                                   if e.kind == "soldier" and e.open is not None and e.open + 45 < info["T"]}'''),
])
print("patched")
