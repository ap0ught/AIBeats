"""Stage 3 (Waterfall) solver: from a savestate one frame before the stage's first frame to stage 4's first frame.

    python -m contra.stages.s3 <state> [--out s3/<name>] [--emus 3] [--prior <inputs.txt>] [--keep 6] [--tests 18]

Phases (no RAM writes anywhere):
    C   the climb: ledge search on the exact model, every node validated in the emulator (s3_climb.py)
    T   the last jump from the top floor that starts the boss scroll
    B   the dragon: survive until the mouth opens, 32 hits, then the exit
See knowledge/s3_notes.md for the mechanism, the numbers and what was tried.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from contra.stages.s3s8_lib import Game, Pad, save_segment, check_rows, read_inputs, LOGS_DIR, STATES_DIR  # noqa: E402
from contra.stages.s3_exec import A_of  # noqa: E402
from contra.stages.s3_climb import Climber, EN  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def drop_in(g: Game, state: str, prior_rows, xs: int, name: str):
    """Play the stage's drop-in, drifting to screen X = xs during the fall. Returns an EN standing on the first
    floor, or None if that X cannot be reached."""
    r = g.load(state, Pad.from_rows(prior_rows))
    n = 0
    while True:
        want = ()
        if r.pstate == 1 and r.x and r.x < xs:
            want = ("Right",)
        elif r.pstate == 1 and r.x > xs:
            want = ("Left",)
        r = g.step(want)
        n += 1
        if r.pstate == 1 and not r.airborne:
            break
        if n > 200:
            return None
    g.e.save(name)
    return EN(len(g.rows), r, name, list(g.rows), g.pad.copy(), None, ("drop", xs), g.lag, g.ignored)


def solve_climb(state: str, tag: str = "s3", emus: int = 3, prior_rows=(), keep: int = 6, tests: int = 18,
                q_end: int = -108, procs: int = 6, starts=(86, 78, 70, 60, 48)):
    (STATES_DIR / tag / "tmp").mkdir(parents=True, exist_ok=True)
    games = [Game(log_name=f"{tag}_g{k}.log") for k in range(emus)]
    cl = Climber(games, tag=tag, procs=procs, log=log)
    t0 = time.time()
    try:
        sts = []
        for k, xs in enumerate(starts):
            en = drop_in(games[0], state, prior_rows, xs, f"{tag}/tmp/start{k}")
            if en is not None:
                sts.append(en)
        log(f"drop-in: {[str(e) for e in sts]}")
        first = sts[0]
        first_others = sts[1:]
        valid = cl.climb(first, q_end, keep=keep, tests=tests, extra_starts=first_others)
        log(f"climb done in {time.time() - t0:.0f}s, {cl.tests} emulator trials")
        return valid, cl, games
    except Exception:
        cl.close()
        for g in games:
            g.close()
        raise


def _boss_and_report(eng, ck, state, out, tag, prior_rows, rep, t0):
    from contra.stages.s3s8_engine import Ck
    from contra.stages import s3_boss
    rows, brep = s3_boss.solve_boss(eng, ck, 0x13, tag)
    rep["events"].update(brep.pop("events"))
    rep.update(brep)
    # the state one frame before the next stage's first frame
    root = Ck(state, 0, [], Pad.from_rows(prior_rows))
    _c, tr = eng.commit(root, rows, keep=f"{out}_next_pre")
    L = next(z["frame"] for z in tr if z["lroutine"] == 4)
    rep["L"] = L
    rep["rows"] = len(rows)
    rep["frames_L_to_next_L"] = len(rows)
    rep["lag_frames"] = [k for k, z in enumerate(tr) if z["lagged"]]
    rep["lag_in_level"] = sum(1 for k in rep["lag_frames"] if k <= rep["events"]["control_lost"])
    rep["deaths"] = sum(1 for k in range(1, len(tr)) if tr[k]["death"] & 1 and not tr[k - 1]["death"] & 1)
    nxt = eng.sim(_c, [()])[0]
    rep["next_first_frame_ok"] = bool(nxt["lroutine"] == 4 and nxt["level"] == 3)
    rep["weapon_out"] = nxt["weapon"]
    rep["wall_seconds"] = round(time.time() - t0)
    return rows, rep


def solve(state: str, out: str = "s3/run", emus: int = 3, prior_rows=(), keep: int = 6, tests: int = 18,
          reuse_climb: bool = False):
    """The whole stage. Returns (rows, report). Saves states/<out>_climb_end and states/<out>_next_pre."""
    from contra.stages.s3s8_engine import Engine, Ck
    from contra.stages import s3_boss
    tag = out.replace("/", "_")
    t0 = time.time()
    rep = {"state": state, "events": {}}
    cj = LOGS_DIR / f"{out}_climb.rows.json"
    if reuse_climb and cj.exists() and (STATES_DIR / f"{out}_climb_end.State").exists():
        # development shortcut: the climb of an earlier run of the same name, only the boss part again
        rows_c = [tuple(x for x in r.split("+") if x) for r in json.loads(cj.read_text())["rows"]]
        rep["events"]["top_floor"] = len(rows_c)
        eng = Engine(emus, tag=tag)
        try:
            ck = Ck(f"{out}_climb_end", len(rows_c), rows_c, Pad.from_rows(list(prior_rows) + rows_c))
            return _boss_and_report(eng, ck, state, out, tag, prior_rows, rep, t0)
        finally:
            eng.close()
    valid, cl, games = solve_climb(state, tag, emus, prior_rows, keep, tests, -108)
    try:
        top = [k for k in valid if k[0] == -108 and valid[k]]
        if not top:
            raise RuntimeError("the climb did not reach the top floor")
        cands = sorted((e for k in top for e in valid[k]), key=lambda e: e.t)
        tops = cands[:6]
        climb_trials = cl.tests
    finally:
        cl.close()
        for g in games:
            g.close()
    eng = Engine(emus, tag=tag)
    try:
        # second pass: the scroll starts when A reaches 1,872 in the jump from the top floor, so a top-floor node
        # that stands higher on the screen (larger A) can start it sooner than one that got there a frame earlier;
        # and the mouth opens on an 8-frame rule, so one row here can be worth eight. Try the trigger jump from
        # each of the earliest top-floor nodes and keep the one whose scroll starts first.
        sel = None
        for en in tops:
            ckc = Ck(en.state, len(en.rows), list(en.rows), Pad.from_rows(list(prior_rows) + list(en.rows)))
            try:
                ck2, info = s3_boss.trigger_jump(eng, ckc, 0x13)
            except RuntimeError:
                continue
            log(f"top-floor node t={en.t} X={en.X} Y={en.Y} A={en.A}: boss scroll would start at row {ck2.i - 1}")
            if sel is None or (ck2.i - 1, en.t) < sel[0]:
                sel = ((ck2.i - 1, en.t), en)
        best = sel[1] if sel else tops[0]
        chain = []
        n = best
        while n is not None:
            chain.append({"t": n.t, "row": n.q, "X": n.X, "Y": n.Y, "sub": n.sub, "A": n.A, "rock": n.rock,
                          "wait": n.how[0] if n.how and n.how[0] != "drop" else 0})
            n = n.parent
        chain.reverse()
        rep["climb_chain"] = chain
        rep["climb_trials"] = climb_trials
        rep["events"]["top_floor"] = best.t
        rep["climb_lag"] = best.lag
        rep["skips"] = sum(1 for a_, b_ in zip(chain, chain[1:]) if a_["row"] - b_["row"] == 4)
        import shutil
        dst = STATES_DIR / f"{out}_climb_end.State"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(STATES_DIR / f"{best.state}.State", dst)
        (LOGS_DIR / f"{out}_climb.rows.json").parent.mkdir(parents=True, exist_ok=True)
        (LOGS_DIR / f"{out}_climb.rows.json").write_text(json.dumps(
            {"state": state, "rows": ["+".join(r) for r in best.rows], "t": best.t, "lag": best.lag}))
        log(f"climb: top floor at row {best.t}, {rep['skips']} skips, lag {best.lag} ({time.time() - t0:.0f}s)")
        rows_c, pad_c = list(best.rows), best.pad
        ck = Ck(f"{out}_climb_end", len(rows_c), rows_c, Pad.from_rows(list(prior_rows) + rows_c))
        return _boss_and_report(eng, ck, state, out, tag, prior_rows, rep, t0)
    finally:
        eng.close()


if __name__ == "__main__":
    args = sys.argv[1:]

    def opt(name, default):
        if name in args:
            i = args.index(name)
            v = args[i + 1]
            del args[i:i + 2]
            return type(default)(v)
        return default
    out = opt("--out", "s3/run")
    emus = opt("--emus", 3)
    keep = opt("--keep", 6)
    tests = opt("--tests", 18)
    prior = opt("--prior", "")
    reuse = "--reuse-climb" in args
    if reuse:
        args.remove("--reuse-climb")
    # rule v2: the sustained press limits (a parameter; default = the rule's) and the real history's last 1,800 rows
    from contra.stages import s3s8_lib
    s3s8_lib.set_windows(s3s8_lib.parse_windows(opt("--windows", "600:109,1800:246")))
    state = args[0] if args else "dbg/s3_pre"
    pr = s3s8_lib.history_tail(read_inputs(prior)) if prior else ()
    rows, rep = solve(state, out, emus, pr, keep, tests, reuse_climb=reuse)
    bad = check_rows(rows, pr)
    rep["input_rule_violations"] = len(bad)
    save_segment(out, rows, {"state": state, "stage": 3, "frames": len(rows)})
    (LOGS_DIR / f"{out}.report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    log(f"DONE: stage 3 = {len(rows)} rows (record 3934); events {rep['events']}; lag {len(rep['lag_frames'])} "
        f"({rep['lag_in_level']} before control is lost); deaths {rep['deaths']}; weapon out ${rep['weapon_out']:02x}; "
        f"next stage first frame reached: {rep['next_first_frame_ok']}; rule violations {len(bad)}")
