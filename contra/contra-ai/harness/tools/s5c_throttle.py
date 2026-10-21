"""Rule v2: show that the searches treat a press the budget refuses as "cannot fire now" (no crash, no illegal row).

    python tools/s5c_throttle.py [run|tank|all]

run   stage 5 from dbg/s5_pre to world X 330 (the first turret man) with the run policy and the repair search,
      three times: rule v2's windows, then a 600-row limit of 30 (the press plan keeps 22 for the tank, so the
      run phase has 8 presses per 600 rows), then a limit of 22 (the plan refuses every press).
tank  the first tank from states/s5/d0_v3_tank1 with the hard budget nearly used up: a pad that already holds
      240 B presses in its last 1,800 rows (one every 7.5 rows), so the fight has 6 presses and then one more
      each time an old one leaves the window: two thirds of the fast fire rate.
Prints rows needed, B presses, rows on which the plan refused, presses the pad refused, and runs check_inputs on
the rows with the same windows.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_inputs  # noqa: E402
from contra.stages import s5  # noqa: E402
from contra.stages.s1_common import Farm, Pad, WINDOWS, log, press_report  # noqa: E402
from contra.stages.s1_engine import Route  # noqa: E402


def run_phase(farm, windows, goal=330):
    g = farm.g0
    g.load_file("dbg/s5_pre", pad=Pad(windows))
    s5.THROTTLED.clear()
    route = Route(s5.JUMPS)
    info = {}
    ok = s5.run_to(farm, g, route, lambda gg: gg.r.prog >= goal or gg.r.lr not in (3, 4), "s5c_thr", info)
    rep = check_inputs.check(g.rows, windows=windows)
    pr = press_report(g.rows, windows=windows)
    log(f"RUN windows {windows}: ok={ok}, world X {g.r.prog} after {len(g.rows)} rows; B {pr}; press plan refused on "
        f"{len([x for x in s5.THROTTLED if x < len(g.rows)])} rows, pad refused {g.pad.refused}; repairs {info.get('repairs')}; "
        f"check_inputs with these windows: {'PASS' if rep['pass'] else 'FAIL'}")
    return ok, len(g.rows)


def tank(farm):
    g = farm.g0
    # a history that leaves 6 presses in the 1,800-row window: 240 presses, one every 7.5 rows
    hist = []
    for k in range(240):
        hist += [("B",), ("B",)] + [()] * (5 if k % 2 else 6)
    pad = Pad.from_rows(hist)
    g.load_file("s5/d0_v3_tank1", pad=pad)
    log(f"TANK: pad holds {g.pad.count('B', 600)} / {g.pad.count('B', 1800)} B presses in its last 600 / 1800 rows, room {g.pad.room('B')}")
    n0 = len(g.rows)
    res = s5.tank_fight3(farm, g, tag="s5c_thr")
    if res is None:
        log("TANK: tank_fight3 found no kill under the throttled budget (no crash); trying the first-pass grid")
        res = s5.tank_fight2(farm, g, tag="s5c_thr")
    rows = hist + [tuple(r) for r in g.rows[n0:]]
    rep = check_inputs.check(rows, windows=WINDOWS)
    log(f"TANK throttled: {'destroyed after ' + str(len(res)) + ' rows' if res is not None else 'not destroyed'} "
        f"(188-189 with a free budget); pad refused {g.pad.refused} presses; B presses in the fight "
        f"{press_report(g.rows[n0:], hist)}; check_inputs --windows on history + fight: {'PASS' if rep['pass'] else 'FAIL'} "
        f"(B most in 600 / 1800: {rep['stats']['B'].get('max_presses_in_600_frames')} / "
        f"{rep['stats']['B'].get('max_presses_in_1800_frames')})")


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    with Farm(3, name="s5c_thr") as farm:
        if what in ("run", "all"):
            for win in (WINDOWS, ((600, 30), (1800, 246)), ((600, 22), (1800, 246))):
                run_phase(farm, win)
        if what in ("tank", "all"):
            tank(farm)


if __name__ == "__main__":
    main()
