"""Second-pass patch 15: trio: the point from which Bill fires becomes a grid parameter (with a soldier wave on
screen the volleys fired from the step make every second frame a lag frame: 70 lag frames in one solve)."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep("def trio_try(c, x_goal, phase, jx, stop_d=16, up_until=0, limit=420):",
    "def trio_try(c, x_goal, phase, jx, stop_d=16, up_until=0, limit=420, fire_from=0):")
rep('''        if (t % 5) == phase and c.can("B"):
            want.add("B")
        if t < up_until:''', '''        if (t % 5) == phase and c.can("B") and f.wx >= fire_from:
            want.add("B")
        if t < up_until:''')
rep('''        for jx in (2612, 2615, 2618, 2621):
            for phase in range(5):
                for stop_d in (17, 22):
                    c.restore(base)
                    try:
                        n = trio_try(c, x_goal, phase, jx, stop_d)
                    except Fail as ex:
                        r.frames_simulated += len(c.rows) - base["n"]
                        res[f"{jx}/{phase}/{stop_d}"] = str(ex)[:8]
                        continue
                    r.frames_simulated += n
                    res[f"{jx}/{phase}/{stop_d}"] = n
                    if best is None or n < best[0]:
                        best = (n, jx, phase, stop_d)''',
    '''        for fire_from in (0, 2646):
            for jx in (2612, 2618):
                for phase in range(5):
                    for stop_d in (17, 22):
                        c.restore(base)
                        try:
                            n = trio_try(c, x_goal, phase, jx, stop_d, fire_from=fire_from)
                        except Fail as ex:
                            r.frames_simulated += len(c.rows) - base["n"]
                            res[f"{fire_from}/{jx}/{phase}/{stop_d}"] = str(ex)[:8]
                            continue
                        r.frames_simulated += n
                        res[f"{fire_from}/{jx}/{phase}/{stop_d}"] = n
                        if best is None or n < best[0]:
                            best = (n, jx, phase, stop_d, fire_from)''')
rep('''        trio_try(c, x_goal, best[2], best[1], best[3])''',
    '''        trio_try(c, x_goal, best[2], best[1], best[3], fire_from=best[4])''')
rep('''    r.user["trio"] = {"rows": best[0], "jump_at": best[1], "phase": best[2], "stop_d": best[3], "all": res}
    r.log(f"[{r.name}] trio: {best[0]} rows to wx {x_goal} (jump at {best[1]}, fire phase {best[2]}, stop at "
          f"{best[3]} px); all: {res}")''',
    '''    r.user["trio"] = {"rows": best[0], "jump_at": best[1], "phase": best[2], "stop_d": best[3],
                      "fire_from": best[4], "all": res}
    r.log(f"[{r.name}] trio: {best[0]} rows to wx {x_goal} (jump at {best[1]}, fire phase {best[2]}, stop at "
          f"{best[3]} px, firing from wx {best[4]}); worst {max(v for v in res.values() if isinstance(v, int))}")''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
