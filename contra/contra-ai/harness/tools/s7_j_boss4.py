"""Job: scripted door fight until scroll frame S0, then the first builder's beam search for the rest."""
from contra.stages import s7, s7b
from contra.stages.s6run import beam_search
from contra.stages.s7b import _fr, grounded, Fail, door_of

f0 = sim.load("s7/ph90_boss_beam")
r = s7.make_runner(sim, route=[], name="bossbeam")
r.aim_mode = "off"
c = r.c
c.stop_on_death = False
base = c.snap()


def score(f, tr, parent):
    if f["bossdef"]:
        return 1000.0
    d = door_of(f)
    sc = 0.0
    if d is not None:
        sc += float(32 - d["hp"]) * 3.0
        for (_, bx, by, br) in f.bullets():
            if br == 1 and d["x"] - 40 < bx < d["x"] + 8 and d["y"] - 30 < by < d["y"] + 40:
                sc += 0.5
    sc += 0.05 * f["x"]
    return sc


for (j1, ph, cut) in ((44, 3, 90), (44, 3, 110), (44, 3, 60), (None, 0, 60)):
    c.restore(base)
    # scripted part until `cut` frames after the scroll starts
    s = -1
    t = 0
    log = []
    try:
        class Stop(Exception):
            pass
        n0 = len(c.rows)
        # run the script frame by frame through boss_try's logic by limiting rows: emulate with limit
        try:
            s7b.boss_try(c, j1, ph, None, limit=24 + cut)
        except Fail:
            pass
        d = door_of(c.f)
        print("script j1", j1, "ph", ph, "cut at s", cut, ": rows", len(c.rows) - n0, "door hp", d["hp"] if d else None,
              "x", c.f["x"], "y", c.f["y"], "dead", c.f.dead)
        if c.f.dead:
            continue
        best = beam_search(r, s7.boss_actions, score, lambda f: bool(f["bossdef"]), s7.boss_key, step=5, width=16,
                           max_steps=40, log=None, label="b")
        print("   beam: total rows", len(c.rows) - n0, "(script alone: 178 / 190)")
    except Exception as ex:      # noqa: BLE001
        print("   failed:", repr(ex))
