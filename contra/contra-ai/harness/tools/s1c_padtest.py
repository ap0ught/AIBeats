"""Unit test of the press budget (contra/stages/s1_common.Pad, rule v2) against check_inputs.check.

    python tools/s1c_padtest.py [--quick]

Part 1 (exact agreement, added 2026-10-16): on every row of random and adversarial press sequences, each of the
Pad's decisions - may button b be newly pressed on this row (can_press), may a held button be released on this
row (can_release) - is compared with check_inputs.check run at its command-line defaults (period 5, hold 2,
release 2, windows 600:109 and 1800:246) on the rows so far plus the candidate row. They must agree exactly, in
both directions (the Pad never refuses what the checker allows and never allows what it refuses). legal() must
return exactly the row those decisions give, and every finished sequence must PASS check_inputs as a whole.
Also run with small windows ((60, 7), (200, 15)) so that both windows bind often and cheaply.

Part 2 (the first version of this test): mashing sequences are throttled to exactly the limits, a Pad built from
the last 2,000 rows of a history decides like one that saw the whole history, and the planning form (Fights).
"""
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_inputs  # noqa: E402
from contra.stages.s1_common import (BTN, Fights, HISTORY_ROWS, HOLD, PERIOD, RELEASE, Pad, WINDOWS,  # noqa: E402
                                     press_report)


def cli_defaults():
    """check_inputs.py's command-line defaults, read from its source (so that this test fails if they change)."""
    src = Path(check_inputs.__file__).read_text(encoding="utf-8")
    num = {k: int(re.search(rf'opt\("--{k}", (\d+)\)', src).group(1)) for k in ("period", "hold", "release")}
    w = re.search(r'opt\("--windows", "([0-9:,]+)"\)', src).group(1)
    num["windows"] = tuple((int(a), int(c)) for a, c in (x.split(":") for x in w.split(",")))
    return num


DEF = cli_defaults()


def checker_allows(rows, cand, b, windows):
    """check_inputs.check's verdict on button b's rules for rows + [cand]. Only the last part of rows is passed:
    it starts on a row where b is not held and is longer than the longest window (+ the 5-frame rule), so b's
    window counts, press period, hold and release are exactly those of the whole list (rows already pass)."""
    span = max([w for w, _ in windows], default=0) + PERIOD + 6
    c = max(0, len(rows) - span)
    while c > 0 and b in rows[c]:
        c -= 1
    rep = check_inputs.check(rows[c:] + [cand], period=DEF["period"], hold=DEF["hold"], release=DEF["release"],
                             buttons=(b,), windows=windows)
    return rep["pass"]


class Wanter:
    """Random and adversarial 'wanted' button sets for B (the budgeted button) and the d-pad / A."""

    def __init__(self, rng: random.Random, mode: str):
        self.r, self.mode, self.k = rng, mode, 0
        self.burst = 0

    def want(self, p: Pad, i: int):
        r, m = self.r, self.mode
        w = set()
        if m == "mash":                     # the fastest cadence, always: the windows bind
            if (p.held["B"] and p.run["B"] < HOLD) or (not p.held["B"]):
                w.add("B")
        elif m == "toggle":                 # wants B on alternate rows: 1-frame presses and 1-frame releases
            if i % 2 == 0:
                w.add("B")
        elif m == "random":
            if r.random() < 0.5:
                w.add("B")
        elif m == "holds":                  # random hold / release lengths 1-6 (many illegal attempts)
            if self.k <= 0:
                self.k = r.randint(1, 6)
                self.burst ^= 1
            self.k -= 1
            if self.burst:
                w.add("B")
        elif m == "edge":                   # mash, then idle until exactly the row the oldest press leaves a window
            if self.burst > 0:
                self.burst -= 1
                if not p.held["B"] or p.run["B"] < HOLD:
                    w.add("B")
            elif p.budget_ok("B") or r.random() < 0.15:
                self.burst = r.choice((1, 2, 3, 5, 9, 40, 200))
                w.add("B")
            elif r.random() < 0.3:
                w.add("B")                  # a press the budget must refuse (or the period rule)
        elif m == "period":                 # presses exactly PERIOD-1 / PERIOD / PERIOD+1 apart, hold 1-3
            if self.k <= 0:
                self.k = r.choice((PERIOD - 1, PERIOD, PERIOD + 1, PERIOD + 2))
                self.burst = r.choice((1, 2, 2, 3))
            self.k -= 1
            if self.burst > 0:
                self.burst -= 1
                w.add("B")
        # other buttons: random presses and holds, opposite directions on purpose sometimes
        for b in ("Up", "Down", "Left", "Right", "A", "Start", "Select"):
            q = 0.5 if b in ("Left", "Right", "Up", "Down") else 0.3
            if r.random() < q * (1.0 if m in ("random", "holds") else 0.4):
                w.add(b)
        return w


def expected_row(p: Pad, want, allows):
    """The row legal(want) must return, from the per-button decisions `allows[b]` of the checker."""
    out = []
    for b in BTN:
        w = b in want
        if w and not p.held[b]:
            if allows[b]:
                out.append(b)
        elif w and p.held[b]:
            out.append(b)
        elif not w and p.held[b]:
            if not allows[b]:               # the release is refused: still held
                out.append(b)
    for a, b in (("Left", "Right"), ("Up", "Down")):
        if a in out and b in out:
            out.remove(a if not p.held[a] else b)
    return tuple(out)


def exact_trial(seed, mode, windows, n_rows, every_other_button=1):
    rng = random.Random(seed)
    p = Pad(windows)
    wt = Wanter(rng, mode)
    rows = []
    stats = {"decisions": 0, "press_ok": 0, "press_refused_rate": 0, "press_refused_budget": 0,
             "release_ok": 0, "release_refused": 0}
    for i in range(n_rows):
        want = wt.want(p, i)
        allows = {}
        for b in BTN:
            if b != "B" and i % every_other_button and b not in want and not p.held[b]:
                continue
            if p.held[b]:
                mine = p.can_release(b)
                theirs = checker_allows(rows, (), b, windows)
                stats["release_ok" if theirs else "release_refused"] += 1
            else:
                mine = p.can_press(b)
                theirs = checker_allows(rows, (b,), b, windows)
                if theirs:
                    stats["press_ok"] += 1
                elif not p.rate_ok(b):
                    stats["press_refused_rate"] += 1
                else:
                    stats["press_refused_budget"] += 1
            stats["decisions"] += 1
            assert mine == theirs, (f"seed {seed} mode {mode} row {i} button {b}: Pad says {mine}, check_inputs says "
                                    f"{theirs}; held {p.held[b]} run {p.run[b]} since {p.since[b]} "
                                    f"in-window {[p.count(b, w) for w, _ in windows]}")
            allows[b] = theirs
        for b in BTN:                       # buttons skipped above (not wanted, not held): no decision needed
            allows.setdefault(b, False)
        row = p.legal(want)
        exp = expected_row(p, want, allows)
        assert row == exp, (seed, mode, i, want, row, exp)
        p.push(row)
        rows.append(row)
        # the copy and a Pad rebuilt from the tail of the rows must hold the same state
        if i % 997 == 996:
            q = Pad.from_rows(rows[-(max([w for w, _ in windows]) + 10):], windows)
            for b in BTN:
                assert q.can_press(b) == p.can_press(b) and q.can_release(b) == p.can_release(b), (seed, i, b)
    rep = check_inputs.check(rows, period=DEF["period"], hold=DEF["hold"], release=DEF["release"], windows=windows)
    bad = {k: v["violations"] for k, v in rep["rules"].items() if v["violations"]}
    assert rep["pass"], (seed, mode, bad)
    most = {w: rep["stats"]["B"].get(f"max_presses_in_{w}_frames") for w, _ in windows}
    return stats, most, p.refused


def exact_tests(quick=False):
    print(f"check_inputs command-line defaults: {DEF}")
    assert DEF["windows"] == WINDOWS and (DEF["period"], DEF["hold"], DEF["release"]) == (PERIOD, HOLD, RELEASE), \
        "s1_common's constants differ from check_inputs.py's defaults"
    modes = ("mash", "edge", "holds", "period", "toggle", "random")
    total = {}
    plans = [(DEF["windows"], 4200 if not quick else 2000, 7)] + [(((60, 7), (200, 15)), 3000 if not quick else 1200, 1)]
    for windows, n, other in plans:
        for k, mode in enumerate(modes):
            seed = 1000 + 17 * k + n
            st, most, refused = exact_trial(seed, mode, windows, n, other)
            for a, v in st.items():
                total[a] = total.get(a, 0) + v
            print(f"  exact: windows {windows} mode {mode:6s} {n} rows: {st['decisions']} decisions agree "
                  f"(presses allowed {st['press_ok']}, refused by the 5-frame rule {st['press_refused_rate']}, by a window "
                  f"{st['press_refused_budget']}; releases allowed {st['release_ok']}, refused {st['release_refused']}); "
                  f"B most per window {most}; legal() dropped {refused} wanted presses for the budget")
    assert total["press_refused_budget"] > 0 and total["release_refused"] > 0 and total["press_refused_rate"] > 0
    print(f"EXACT AGREEMENT: {total['decisions']} decisions, all equal to check_inputs.check at its defaults")


def budget_tests():
    random.seed(7)
    for trial in range(8):
        win = WINDOWS if trial < 4 else ((60, 7), (200, 15))
        p = Pad(win)
        rows = []
        for i in range(7000):
            w = set()
            mode = trial % 4
            if (mode == 0 and ((p.held['B'] and p.run['B'] < 2) or p.rate_ok('B'))) or (mode == 1 and random.random() < 0.9) or (mode == 2 and (i % 5) < 2) or \
                    (mode == 3 and (i // 700) % 2 == 0):
                w.add("B")
            if random.random() < 0.3:
                w.add(random.choice(["Up", "Down", "Left", "Right", "A"]))
            r = p.legal(w)
            p.push(r)
            rows.append(r)
        rep = check_inputs.check(rows, windows=win)
        pr = press_report(rows, windows=win)
        bad = {k: v["violations"] for k, v in rep["rules"].items() if v["violations"]}
        print(f"trial {trial} windows {win}: pass {rep['pass']} {pr} refused {p.refused} {bad}")
        assert rep["pass"], bad
        for wf, wmax in win:
            assert pr[f"most_{wf}"] <= wmax
            assert rep["stats"]["B"][f"max_presses_in_{wf}_frames"] == pr[f"most_{wf}"]
        if trial % 4 in (0, 2):
            assert pr[f"most_{win[-1][0]}"] == win[-1][1], "a mash must fill the longest window exactly"
        # a Pad from the tail of the history decides like the Pad that saw everything
        q = Pad.from_rows(rows[-HISTORY_ROWS:], win) if win == WINDOWS else Pad.from_rows(rows[-400:], win)
        for i in range(2500):
            w = {"B"} if random.random() < 0.8 else set()
            a, b = p.legal(w), q.legal(w)
            assert a == b, (i, a, b)
            p.push(a)
            q.push(b)
    # planning form: with a fight of 30 presses 100 rows ahead the run phase is refused 30 presses early
    p = Pad()
    f = Fights([(1000, 30)])
    n = 0
    for i in range(900):
        w = {"B"} if (p.held["B"] and p.run["B"] < 2) or (p.rate_ok("B") and f.room(p, i)) else set()
        r = p.legal(w)
        n += "B" in r and not p.held["B"]
        p.push(r)
    print("presses allowed in 900 rows before a fight that needs 30:", n, "| in the last 600:", p.count("B", 600),
          "| room left:", p.room("B"))
    assert p.count("B", 600, 100) + 30 <= 109 and p.room("B", 100) >= 30


def main():
    exact_tests(quick="--quick" in sys.argv)
    budget_tests()
    print("OK")


if __name__ == "__main__":
    main()
