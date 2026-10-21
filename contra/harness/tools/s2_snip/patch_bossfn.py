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
    ("    b = bb.solve_boss(S, width=boss_width, hold=boss_hold, **boss)\n",
     "    b = (boss[\"fn\"](S, width=boss_width, hold=boss_hold) if \"fn\" in boss\n         else bb.solve_boss(S, width=boss_width, hold=boss_hold, **boss))\n"),
])
patch("contra/stages/s4.py", [
    ("from . import s2\n", "from . import base_boss4, s2\n"),
    ('BOSS = dict(final_type=0x1C, hp_field="e4", hp_full=10, moving=False)    # helmets: real HP in ENEMY_VAR_4',
     'BOSS = dict(fn=base_boss4.solve_boss)     # platings by beam, helmets (real HP in ENEMY_VAR_4) by a scripted attack'),
])
print("patched")
