"""Stage 2 (Base 1) solver: five rooms (base_room.RoomSolver) + the boss + the exit.

The boss fight is planned on an exact offline model of the boss screen and executed closed-loop
(base_bsim / base_bplan / base_bfight, second pass 2026-10-12); the first builder's emulator beam search
(base_boss) is kept as the fallback. The planner uses worker processes: call solve() from an import-safe script.

    from contra.stages import s2
    out = s2.solve(emu, "ref_s2", hist=rows_before)      # state = the stage's first frame ($2C == 4)

out["rows"] = the legal input segment up to and including the next stage's first frame; per-room results.
Stage 4 (s4.py) uses the same driver with its own boss parameters.
"""
from __future__ import annotations

from . import base_bfight as bf
from . import base_fight3 as bf3
from . import base_boss as bb
from .base_common import Sess, make_fields
from .base_room import RoomSolver
from .base_room3 import RoomSolver3

OLD_BOSS = dict(final_type=0x10, hp_field="e1", hp_full=16, moving=True)     # the Eye: real HP in ENEMY_VAR_1


def planned_boss(old):
    """Boss function: the fight planned on the offline model (base_bfight); if that fails, the first builder's
    emulator beam search `old(S, width=, hold=)` from the same state."""
    def fn(S, width=12, hold=4, **_):
        snap = S.snapshot()
        try:
            info = bf3.solve_boss(S)        # third pass: base_bfight's executor + the cheap lost-read repair
        except Exception as ex:  # noqa: BLE001
            import traceback
            info = {"ok": False, "why": traceback.format_exc()[-1500:]}
        if info.get("ok"):
            info["method"] = "offline model plan"
            return info
        S.restore(snap)
        b = old(S, width=width, hold=hold)
        b["method"] = "fallback: emulator beam"
        b["planned_failed"] = info.get("why")
        return b
    return fn


def _old_eye(S, width=12, hold=4, **_):
    snap_b = S.snapshot()
    best_b, bi = None, None
    tried = []
    for w, h in ((20, 4), (width, hold), (16, 3)):
        S.restore(snap_b)
        bi = bb.solve_boss(S, width=w, hold=h, **OLD_BOSS)
        tried.append((w, h, bi.get("frames"), bi.get("ok")))
        if bi["ok"] and (best_b is None or bi["frames"] < best_b[0]["frames"]):
            best_b = (bi, S.snapshot())
    if best_b:
        S.restore(best_b[1])
        bi = best_b[0]
    bi["variants"] = tried
    return bi


BOSS = dict(fn=planned_boss(_old_eye))


def solve(emu, state, hist=(), verbose=True, beam=12000, save_states=None, boss_width=12, boss=None, rooms_only=False,
          boss_hold=4, pause=0, rooms3=True):
    boss = boss or BOSS
    S = Sess(emu, hist=hist, fields=make_fields())
    S.load(state)
    f0 = S.s["frame"]
    out = {"start_frame": f0, "rooms": [], "fc0": S.s["frame_fc"], "rng0": S.s["rng"], "ok": False}
    if S.s["lroutine"] != 4:
        raise ValueError("the start state must be the stage's first frame ($2C == 4)")
    if pause:
        # a different start condition for testing: pause for `pause` frames before the first room's logic starts
        # (shifts the frame counter and the random number relative to everything in the stage; costs its length)
        S.step(("Start",))
        S.step(("Start",))
        for _ in range(max(2, pause - 2)):
            S.step(())
        S.step(("Start",))               # logic resumes on this frame: T = 0
        out["pause_rows"] = len(S.rows) - 1
    else:
        S.step(())                       # the room's enemies appear on the next frame: T = 0
    # third pass (2026-10-12): the rooms are driven by base_room3 (entry x chosen, hop steered, walking shots,
    # lost controller reads handled); the first builder's driver is the fallback for a room it cannot do
    rs = RoomSolver3(S, verbose=verbose, beam=beam) if rooms3 else None
    rs_old = RoomSolver(S, verbose=verbose, beam=beam)
    room = 0
    prev = None
    while not (S.s["loc"] & 0x80):
        room += 1
        snap0 = S.snapshot()
        n_before = len(S.rows)
        driver = "base_room3"
        R = None
        if rs is not None:
            try:
                R = rs.solve(snap0, prev=prev, save_as=f"{save_states}/room{room}" if save_states else None)
                n_before = getattr(R, "n_load", n_before)
            except Exception:  # noqa: BLE001
                import traceback
                if verbose:
                    print("base_room3 failed:", traceback.format_exc()[-1500:], flush=True)
                R = None
        if R is None or not R.ok:
            if rs is not None and verbose:
                print(f"room {room}: base_room3 gave {getattr(R, 'reason', 'an exception')}; using the first driver", flush=True)
            snap_o = getattr(R, "snap0", None) or snap0
            S.restore(snap_o)
            n_before = len(S.rows)
            if save_states:
                emu.save(f"{save_states}/room{room}")
            driver = "base_room"
            R = rs_old.solve(snap_o)
        elif R.lag >= 3:
            # a room with lag frames (stage 2 room 4: six rollers, four soldiers and ten bullets): each costs a whole
            # frame and the planners do not model them, so the first driver's plan is played too and the shorter
            # room is kept (measured 2026-10-12: 500 rows with 12 lag frames against 492 with 4)
            end_new = S.snapshot()
            S.restore(R.snap0)
            R2 = rs_old.solve(R.snap0)
            if R2.ok and len(S.rows) < len(end_new[1]):
                if verbose:
                    print(f"room {room}: first driver {len(S.rows) - n_before} rows (lag {R2.lag}) against "
                          f"{len(end_new[1]) - n_before} (lag {R.lag}): kept", flush=True)
                if getattr(R, "tail", None):
                    try:
                        emu.mfree(R.tail["snap"][0])
                    except Exception:  # noqa: BLE001
                        pass
                R, driver = R2, "base_room (fewer lag frames)"
            else:
                if verbose:
                    print(f"room {room}: first driver {len(S.rows) - n_before if R2.ok else 'failed'} rows (lag "
                          f"{R2.lag}) against {len(end_new[1]) - n_before} (lag {R.lag}): base_room3 kept", flush=True)
                S.restore(end_new)
        if prev is not None:
            try:
                emu.mfree(prev["snap"][0])
            except Exception:  # noqa: BLE001
                pass
        prev = getattr(R, "tail", None)
        out["rooms"].append({"room": room, "ok": R.ok, "reason": R.reason, "load": n_before, "last_hit_T": R.T_last_hit,
                             "cleared_T": R.T_cleared, "next_T": R.T_next, "lag": R.lag, "replans": R.replans,
                             "frames": len(S.rows) - n_before, "driver": driver,
                             "plan_secs": round(getattr(R, "plan_secs", 0)), "lost_reads": getattr(R, "lost", None),
                             "plan": [(p[0], p[1], p[5], [h[0] for h in p[4]]) for p in R.plan.presses] if R.plan else None,
                             "ents": [repr(e) for e in getattr(R, "ents", [])][:12]})
        if verbose:
            print(f"room {room}: {out['rooms'][-1]['frames']} frames, last hit T{R.T_last_hit}, lag {R.lag}, "
                  f"replans {R.replans} {R.reason}", flush=True)
        out["rows"] = list(S.rows)
        if not R.ok:
            return out
        S.free()
    if save_states:
        emu.save(f"{save_states}/boss")
    out["boss_load"] = len(S.rows)
    if rooms_only:
        return out
    if "fn" in boss:
        b = boss["fn"](S, width=boss_width, hold=boss_hold)
    else:
        # the beam search is greedy and its result moves by tens of frames with its width: run a few, keep the best
        snap_b = S.snapshot()
        best_b = None
        tried = []
        for w, h in ((20, 4), (boss_width, boss_hold), (16, 3)):
            S.restore(snap_b)
            bi = bb.solve_boss(S, width=w, hold=h, **boss)
            tried.append((w, h, bi.get("frames"), bi.get("ok")))
            if bi["ok"] and (best_b is None or bi["frames"] < best_b[0]["frames"]):
                best_b = (bi, S.snapshot())
        if best_b:
            S.restore(best_b[1])
            b = best_b[0]
        else:
            b = bi
        b["variants"] = tried
    out["boss"] = b
    out["rows"] = list(S.rows)
    if verbose:
        print("boss:", b, flush=True)
    if not b["ok"]:
        return out
    out["boss_dead"] = len(S.rows)
    if save_states:
        emu.save(f"{save_states}/boss_dead")
    x = bb.solve_exit(S)
    out["exit"] = x
    out["ok"] = x["ok"]
    out["rows"] = list(S.rows)
    out["frames"] = len(S.rows)
    out["end_frame"] = S.s["frame"]
    out["weapon"] = S.s["weapon"]
    out["lives"] = S.s["lives"]
    if save_states and x["ok"]:
        emu.save(f"{save_states}/next_stage")
    return out
