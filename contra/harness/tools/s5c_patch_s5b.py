"""Third one-off patch for rule v2, stage 5 only: the other tank parity.

A tank's arrival moves in 2-frame steps (its own scroll runs on odd frame-counter frames), so reaching it one
frame earlier or later than the old solver changes which drive-in / kill-jump scripts are best, and measured on
dbg/s5_pre arriving ONE FRAME EARLIER ended two frames later after tank 2. solve() now also tries each tank with
one extra jump about 88 px before it (one frame later, another Y sub-pixel) and keeps whichever has the scroll
60 px past the tank on the earlier row. Fail-safe: any error in the alternative keeps the plain result."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s5.py"
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('''    st = g.save_file(f"tmp/{tag}_tank")
    pad, keep = g.pad.copy(), list(g.rows)
    scr0 = g.r.scr

    def ev1(gg, job):
''', '''    st = g.save_file(f"tmp/{tag}_tank")
    pad, keep = g.pad.copy(), list(g.rows)
    scr0 = g.r.scr
    tank_fight3.last = None          # (rows until the scroll is 60 px past the stop, rows until its HP is 0) of the fight played

    def ev1(gg, job):
''')
rep('''    n = tank_script2(g, *jobs2[ok2[0][1]])
    assert n == ok2[0][0][1], (n, ok2[0])
    return g.rows[len(keep):]
''', '''    n = tank_script2(g, *jobs2[ok2[0][1]])
    assert n == ok2[0][0][1], (n, ok2[0])
    tank_fight3.last = ok2[0][0]
    return g.rows[len(keep):]


tank_fight3.last = None
''')
rep('''def run_to(farm: Farm, g: Game, route: Route, done, tag, info):
    rep = Repair5(farm, policy, fail, tag=tag, local=local_beam(policy, fail_hard, tag=tag, shoot=shoot_planned),
                  engage=engage, fail_look=fail_hard, sight=sight)
''', '''def run_to(farm: Farm, g: Game, route: Route, done, tag, info, pre=None, trig=None):
    """pre / trig: keep a file state of the main run about 88 px before world X `trig` (the next tank) in the
    dict `pre` (state, pad, rows), for solve()'s try of the other tank parity."""
    def mark(gg):
        if pre is not None and trig is not None and not gg.r.air and trig - 92 <= gg.r.prog < trig - 84:
            pre.update(state=gg.save_file(f"tmp/{tag}_pretank"), pad=gg.pad.copy(), rows=list(gg.rows))
        return None
    rep = Repair5(farm, policy, fail, tag=tag, local=local_beam(policy, fail_hard, tag=tag, shoot=shoot_planned),
                  engage=engage, fail_look=fail_hard, sight=sight, mark=mark)
''')
rep('''        ntank = 0
        while True:
            ok = run_to(farm, g, route, lambda g: tank_state(g.r)[0] == "drive" or g.r.auto > 0 or g.r.lr not in (3, 4),
                        f"s5_{out}_run{ntank}", info)
            save_seg(f"s5/{out}_partial", g.rows, info)
            if not ok:
                return None
            if g.r.auto > 0:
                break
            ntank += 1
            info["marks"][f"tank{ntank}_created"] = len(g.rows)
            g.save_file(f"s5/{out}_tank{ntank}")
            t1 = time.time()
            res = tank_fight3(farm, g, tag=f"s5_{out}")
''', '''        ntank = 0
        to_tank = lambda g: tank_state(g.r)[0] == "drive" or g.r.auto > 0 or g.r.lr not in (3, 4)     # noqa: E731
        while True:
            pre = {}
            trig = next((x for x, _ in PLAN.fights[:2] if x > g.r.prog + 100), None)
            ok = run_to(farm, g, route, to_tank, f"s5_{out}_run{ntank}", info, pre=pre, trig=trig)
            save_seg(f"s5/{out}_partial", g.rows, info)
            if not ok:
                return None
            if g.r.auto > 0:
                break
            ntank += 1
            created = len(g.rows)
            g.save_file(f"s5/{out}_tank{ntank}")
            t1 = time.time()
            res = tank_fight3(farm, g, tag=f"s5_{out}")
            if res is not None and tank_fight3.last is not None and pre and parity:
                # the other parity: one extra jump before the tank (one frame later, another Y sub-pixel)
                plain = (g.save_file(f"tmp/s5_{out}_tankplain"), g.pad.copy(), list(g.rows))
                best_abs, taken = created + tank_fight3.last[0], False
                try:
                    g.load_file(pre["state"], pre["pad"], rows=pre["rows"])
                    route2 = route.copy()
                    route2.opts["dec"] = list(route.opts.get("dec", ()))
                    route2.add_over(len(g.rows), ("add", "A"))
                    route2.add_over(len(g.rows) + 1, ("add", "A"))
                    info2 = {}
                    if run_to(farm, g, route2, to_tank, f"s5_{out}_run{ntank - 1}p", info2) and tank_state(g.r)[0] == "drive":
                        created2 = len(g.rows)
                        g.save_file(f"tmp/s5_{out}_tankalt")
                        res2 = tank_fight3(farm, g, tag=f"s5_{out}")
                        alt_abs = None if res2 is None or tank_fight3.last is None else created2 + tank_fight3.last[0]
                        log(f"tank {ntank}: scroll 60 px past it on row {best_abs} as it came (created on row {created}); "
                            f"with one extra jump before it on row {alt_abs} (created on row {created2})")
                        if alt_abs is not None and alt_abs < best_abs:
                            taken = True
                            route, created, res = route2, created2, res2
                            info.setdefault("repairs", []).extend(info2.get("repairs", []))
                            info["run_presses"] = info.get("run_presses", 0) + info2.get("run_presses", 0)
                            info["lag_run"] = info.get("lag_run", 0) + info2.get("lag_run", 0)
                            info.setdefault("tank_parity_jump", []).append(ntank)
                            shutil.copyfile(STATES_DIR / "tmp" / f"s5_{out}_tankalt.State",
                                            STATES_DIR / "s5" / f"{out}_tank{ntank}.State")
                except Exception as ex_:                 # noqa: BLE001
                    log(f"tank {ntank}: the try of the other parity failed ({ex_!r}); keeping the plain fight")
                    taken = False
                if not taken:
                    g.load_file(plain[0], plain[1], rows=plain[2])
            info["marks"][f"tank{ntank}_created"] = created
''')
rep('''def solve(start="dbg/s5_pre", out="d0", n=3, history=None, width=8):
''', '''def solve(start="dbg/s5_pre", out="d0", n=3, history=None, width=8, parity=True):
''')
rep('''import json
import math
import subprocess
import sys
import time

from ..emulator import LOGS_DIR, PROJECT
''', '''import json
import math
import shutil
import subprocess
import sys
import time

from ..emulator import LOGS_DIR, PROJECT, STATES_DIR
''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("s5.py patched (tank parity)")
