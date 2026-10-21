"""Plan a UFO fight in the offline model for one jump lead and compare it frame by frame with the emulator."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s5, s5_ufo_sim  # noqa: E402
from contra.stages.s1_common import Game  # noqa: E402

state, lead, width = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
g = Game(name="s5b_ufocmp")
try:
    g.load_file(state)
    th, k0 = 102, 57
    while True:
        k = len(g.rows)
        r = g.r
        e = s5.ufo(r)
        tx = e[4]
        if k >= k0 and r.x == tx and g.pad.held["Up"]:
            break
        w = set()
        if not (e[4] == 240 and k < 8):
            if r.x < tx:
                w.add("Right")
            elif r.x > tx:
                w.add("Left")
            else:
                w.add("Up")
        g.step(w)
    k0 = len(g.rows)
    r = g.r
    acc = [(r.m[0x3A8 + s], r.m[0x398 + s]) for s in range(10)]
    args = (k0, r.y * 256 + r.m[0x94], r.x, acc, th, e[4], 48)
    kw = dict(a.split("=") for a in sys.argv[4:])
    res = s5_ufo_sim.plan(*args, th - lead, width=width, **{k_: int(v) for k_, v in kw.items()})
    print("plan", res[0] - th, res[1], res[2])
    sim = s5_ufo_sim.replay(*args, res[1], res[2], res[0] + 12, **{k_: int(v) for k_, v in kw.items() if k_ == "bombs"})
    sched = s5.UfoSchedule(None, g.pad, [])
    sched.pad0 = g.pad.copy()
    sched.k0 = k0
    sched.prefix = []
    rows = sched.rows(res[1], res[2], res[0] + 12)
    sm = s5_ufo_sim.Sim(args[0], args[1], args[2], args[3], 32, th, args[5], args[6])
    PP, JJ = set(res[1]), set(res[2])
    for (k, y, hp), row in zip(sim, rows):
        sm.step((sm.k + 1) in PP, (sm.k + 1) in JJ)
        r = g.step_raw(row)
        mb = [(i, b[1] >> 8, b[2] >> 8, b[0]) for i, b in enumerate(sm.sl) if b is not None]
        eb = [(b[0], b[1], b[2], b[3]) for b in r.bullets()]
        if mb != eb and k >= th - 12:
            print("   k=%d BULLETS model %s" % (k, mb))
            print("              emu   %s" % (eb,))
        e = s5.ufo(r)
        ehp = e[3] if e else -1
        flag = "" if (y, hp) == (r.y, ehp) else "  <-- differs"
        if k >= th - 2:
            print(f"k={k} model y={y} hp={hp} | emu y={r.y} hp={ehp} nb={r.nbullets()} {'+'.join(row):6s} "
                  f"E={[(x[0], x[1], x[4], x[5], x[3]) for x in r.enemies() if x[1] != 0x14]}{flag}"
                  + (f" B={[(b[0], b[1], b[2], b[3]) for b in r.bullets()]} ufo={e}" if k >= 160 else ""))
        if ehp <= 0:
            break
finally:
    g.close()
