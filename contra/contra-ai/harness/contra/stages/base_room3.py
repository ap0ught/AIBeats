"""Third-pass room driver for the two bases (2026-10-12): base_room's closed loop (record the room, plan on the
abstract model, execute, re-plan with a new constraint when the emulator disagrees, fence, walk in) on the planner
base_plan3, which adds what the first driver did not use:

* the x Bill ENTERS a room with is chosen: while the previous room clears (59 frames after its last hit) he walks to
  the x the next room's plan wants (`solve(..., prev=tail of the previous room)` walks that room's exit again);
* the 50-frame hop (and the stage-start drop) is steered with a 2-frame tap;
* he walks while B is held; every plan comes with a frame-by-frame walk that obeys the d-pad rules;
* a controller read the game loses (NesHawk's DMC conflict: the game re-uses the previous frame's buttons) is seen
  on the frame it happens ($F1 against the row sent); if it changes anything, only the rest of the room is planned
  again and everything played before that row stays as it was.

T = frames since the room's enemies appeared (T = 0: the frame `screen` changed / the stage's first frame + 1);
"row T" is the input row that produces the state at T.
"""
from __future__ import annotations

import time

from . import base_plan3 as bp
from .base_common import BIT, Sess, bullets
from .base_room import RoomResult, move_script, record_room

REACH = 66          # px Bill can walk between a room's last press and the frame the room is cleared (76 frames)
MAX_DEATHS = 10     # death attempts in one room before it is given to the first driver (2026-10-16: stage 4 room 4
                    # from s4/dbg_L died 32 times at x 127, one frame later each time, for 18 minutes; the verified
                    # runs needed at most 4)
LR = BIT["Left"] | BIT["Right"]


class RoomSolver3:
    def __init__(self, S: Sess, verbose=True, beam=12000, ntop=6, max_replans=30, keep=2, choose_entry=True):
        self.S, self.verbose, self.beam, self.ntop, self.max_replans = S, verbose, beam, ntop, max_replans
        self.keep = keep
        self.choose_entry = choose_entry
        self.back = 24

    def say(self, *a):
        if self.verbose:
            print(*a, flush=True)

    def jump_table(self, snap0, T_land):
        """Player Y at the end of each frame of a standing jump (index 0 = the frame A is first read)."""
        S = self.S
        S.restore(snap0)
        T = 0
        while T < T_land + 2:
            if not S.step(S.pad.fix(()))["lagged"]:
                T += 1
        ys = []
        for i in range(80):
            s = S.step(S.pad.fix(("A",) if i < 2 else ()))
            if s["lagged"]:
                continue
            ys.append(s["y"])
            if i > 3 and not s["jump"]:
                break
        S.restore(snap0)
        return ys[:-1] if ys else None

    # -- the input rows of a plan -----------------------------------------------------------------------------
    def build_rows(self, plan, T_land, entry, avoid=(), jump_len=0, force=None, lost=()):
        """(rows, pos, dpad, path): rows[T] (T = 1 .. last press + FLIGHT + 1) for a plan from the entry (px,
        facing), or (None, bad press index, None, None)."""
        presses = plan.presses
        dpad, pos, path = bp.walk_rows(presses, T_land + 1, [entry], t0=2, avoid=avoid, jump_len=jump_len, force=force,
                                       lost=lost)
        if dpad is None:
            return None, pos, None, None
        T_end = presses[-1][0] + bp.FLIGHT + 1
        rows = {T: set() for T in range(1, T_end + 1)}
        for T, b in dpad.items():
            if b and T in rows:
                rows[T].add(b)
                if T <= T_land and T + 1 in rows:      # a drift tap in the air: held two frames
                    rows[T + 1].add(b)
        need_down = set()
        no_down = set()
        for (T, k, mR, mL, hk, pose) in presses:
            for q in (T, T + 1):
                if q not in rows:
                    continue
                if pose == 9:
                    rows[q].add("A")
                    no_down.add(q)
                else:
                    rows[q].add("B")
                    if pose == 1:
                        rows[q].add("Down")
                        need_down.add(q)
                    else:
                        no_down.add(q)
            if pose == 9:
                no_down.update(range(T, T + jump_len + 2))
        # idle crouch: Down on ground rows with nothing else to do (it is what keeps Bill under the bullets), in
        # holds of >= 2 frames that leave every crouch shot's own Down press legal (released >= 2, starts >= 5 apart)
        ok_rows = [T for T in range(T_land + 1, T_end + 1) if (not rows[T] and T not in no_down) or T in need_down]
        runs = []
        for T in ok_rows:
            if runs and runs[-1][1] == T - 1:
                runs[-1][1] = T
            else:
                runs.append([T, T])
        chosen = []          # [start, end, [must pairs]] of Down holds, in order
        for a, b in runs:
            musts = sorted(q for q in need_down if a <= q <= b)
            pairs = [(q, q + 1) for q in musts if q - 1 not in need_down]
            q0 = musts[0] if musts else None

            def first_start():
                if not chosen:
                    return a
                return max(a, chosen[-1][1] + 3, chosen[-1][0] + 5)
            s0 = first_start()
            if q0 is not None and s0 > q0:
                # the hold before this one is in the way of a crouch shot: cut it down to its own crouch shots
                ps, pe, pp = chosen.pop()
                for (u, v) in pp:
                    chosen.append([u, v, [(u, v)]])
                s0 = min(first_start(), q0)
            if s0 > b or (q0 is None and b - s0 + 1 < 2):
                continue
            chosen.append([s0, b, pairs])
        for s0, b, _ in chosen:
            for T in range(s0, b + 1):
                rows[T].add("Down")
        order = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
        out = {T: tuple(x for x in order if x in r) for T, r in rows.items()}
        return out, pos, dpad, path

    # -- one attempt at a plan -------------------------------------------------------------------------------
    def execute(self, snap0, plan, ents, T_land, entry, avoid=(), jump_len=0, force=None, lost=()):
        """Returns (status, info). status: 'ok' | 'nopath' | 'nopress' | 'lost' | 'miss' | 'extra' | 'death' | 'pos'."""
        S = self.S
        s = S.restore(snap0)
        presses = plan.presses
        cores = [e for e in ents if e.kind == "core"]
        res = {"hits": [], "lag": 0, "lost_seen": []}
        rows, pos, dpad, path = self.build_rows(plan, T_land, entry, avoid, jump_len, force, lost)
        if rows is None:
            res["T"] = presses[pos][0]
            return "nopath", res
        res["dpad"], res["path"] = dpad, path
        # the rows must be legal as they are (the pad state at the room's start is the session's)
        pad = S.pad.copy()
        for T in sorted(rows):
            if not pad.ok(rows[T]):
                # a button from before the room that must still be held (Start after a pause, Up from the walk-in)
                fx = pad.fix(rows[T])
                if pad.ok(fx) and set(fx) ^ set(rows[T]) <= {"Start", "Select", "Up"}:
                    rows[T] = fx
            if not pad.ok(rows[T]):
                nxt = [p[0] for p in presses if p[0] >= T]
                res.update(T=nxt[0] if nxt else presses[-1][0], why=f"illegal row {rows[T]} at T{T}")
                return "pos", res
            pad.push(rows[T])
        by_t = {p[0]: i for i, p in enumerate(presses)}
        pending = []         # (arrival T, expected hits, press index)
        T_end = presses[-1][0] + bp.FLIGHT + 1
        last_hit_T = None
        T = 0
        while T < T_end:
            row = rows[T + 1]
            sp = s
            s = S.step(row)
            while s["lagged"]:            # lag frame: the game did nothing and read nothing; same row again
                res["lag"] += 1
                s = S.step(S.pad.fix(row))
            T += 1
            if s["death"] & 1:
                res["T"] = T
                res["x"] = s["x"]
                return "death", res
            pi = by_t.get(T)
            sent = sum(BIT[b] for b in row)
            if s["pad"] != sent and T >= 2:
                # the game did not read the pad on this row (it re-used the previous row's buttons)
                res["lost_seen"].append(T)
                if (s["pad"] ^ sent) & LR or pi is not None:
                    res.update(T=T, seen=s["pad"], sent=sent)
                    return "lost", res
            if pi is not None:
                (pT, k, mR, mL, hk, pose) = presses[pi]
                if k == 0:
                    if not s["jump"]:
                        res.update(T=T, why="no jump")
                        return "nopress", res
                else:
                    new = [b for b in bullets(s) if b[2] == 21]
                    face = 1 if s["aim"] >= 5 else 0
                    if len(new) != k or (pose < 2 and new and new[0][5] != (156 if pose else 144)):
                        res.update(T=T, got=len(new), want=k, y=new[0][5] if new else None, x=s["x"], pad=s["pad"])
                        return "nopress", res
                    xb = sp["x"]
                    m = mL if (face and pose < 2) else mR
                    if not (bp.PXMIN <= xb <= bp.PXMAX and (m >> (xb - bp.PXMIN)) & 1):
                        res.update(T=T, x=xb, face=face, want=pos.get(pi))
                        return "pos", res
                    pending.append((T + bp.FLIGHT, hk, pi))
            if T == presses[-1][0] + 2:
                res["tail"] = (S.snapshot(), T, s["x"])
            if pending and pending[0][0] == T:
                _, hk, idx = pending.pop(0)
                got = []
                for i in range(16):
                    hb, ha = sp[f"eh{i}"], s[f"eh{i}"]
                    if sp[f"er{i}"] and sp[f"et{i}"] == s[f"et{i}"] and (
                            (0 < hb < 0xF0 and ha == hb - 1) or (s[f"et{i}"] == 0x14 and hb == 0 and ha in (4, 7))):
                        p2 = (s[f"ex{i}"], s[f"ey{i}"])
                        m = [e for e in ents if e.etype == s[f"et{i}"] and T in e.track and e.track[T][:2] == p2]
                        got.append(m[0].eid if m else -1 - i)
                        if not m:
                            res.setdefault("unk", []).append((T, i, hex(s[f"et{i}"]), p2, [(e.eid, e.track[T][:2]) for e in ents if e.etype == s[f"et{i}"] and T in e.track]))
                exp = sorted(h[0] for h in hk)
                if sorted(got) != exp:
                    res.update(T=T, got=sorted(got), want=exp, press=presses[idx][0])
                    return ("miss" if set(exp) - set(got) else "extra"), res
                for c in cores:
                    if c.eid in got:
                        last_hit_T = T
        res["T_last_hit"] = last_hit_T
        res["cores_left"] = s["cores"]
        return "ok", res

    # -- after the last hit: (walk to the next room's entry x,) fence and walk in ------------------------------
    def _walk(self, T, man=None, target=None):
        """Crouch until the room is cleared, then hold Up until the next room appears. man = optional dodge:
        ("jump", i) | ("Left"/"Right", i, n) | ("stand", i, n) applied at step i; target = x to walk to first.
        Returns (T_cleared, T_next, None) or (None, None, step of death). The session is left on the next room's
        T = 0 frame."""
        S = self.S
        s = S.s
        scr = s["screen"]
        Tc = None
        script = []
        if target is not None and target != s["x"]:
            face = 1 if s["aim"] >= 5 else 0
            script = [list(x) for x in move_script(s["x"], face, target, 1 if target < s["x"] else 0)]
        for i in range(460):
            if script:
                row = (script[0][0],)
                script[0][1] -= 1
                if script[0][1] == 0:
                    script.pop(0)
            elif s["cleared"] == 0:
                row = ("Down",)
                if man:
                    if man[0] == "jump" and man[1] <= i < man[1] + 2:
                        row = ("A",)
                    elif man[0] in ("Left", "Right") and man[1] <= i < man[1] + man[2]:
                        row = (man[0],)
                    elif man[0] == "stand" and man[1] <= i < man[1] + man[2]:
                        row = ()
            else:
                row = ("Up",)
                if Tc is None:
                    Tc = T
            s = S.step(S.pad.fix(row))
            T += 1
            if s["death"] & 1:
                return None, None, i
            if s["screen"] != scr:
                return Tc, T, None
        return None, None, 460

    def walk(self, T, tail=None):
        S = self.S
        Tc, Tn, d = self._walk(T)
        if d is None:
            return Tc, Tn
        if tail is None:
            return None
        snap, Tt = tail[0], tail[1]
        d += T - Tt                      # step of death counted from the tail snapshot
        self.say(f"   walk: death {d} frames after the last press, searching a dodge")
        best = None
        cands = [("jump", d - j) for j in range(2, 50, 2) if d - j >= 0]
        cands += [(b, d - j, n) for b in ("Left", "Right") for n in (4, 8, 12, 16, 24, 32) for j in (n + 1, n + 6, n + 12) if d - j >= 0]
        cands += [("stand", d - j, n) for n in (4, 8, 16) for j in (2, 4, 8) if d - j >= 0]
        for man in cands:
            S.restore(snap)
            Tc, Tn, d2 = self._walk(Tt, man)
            if d2 is None and (best is None or Tn < best[1]):
                best = (man, Tn)
                if Tn - Tt <= 196 + 18:
                    break
        if best is None:
            return None
        S.restore(snap)
        Tc, Tn, d2 = self._walk(Tt, best[0])
        self.say(f"   walk: dodge {best[0]} -> next room at T{Tn}")
        return Tc, Tn

    def rewalk(self, prev, want_x):
        """Walk the previous room's exit again so that Bill enters this room at want_x. prev = dict(snap, T, x,
        T_next). Returns the new T = 0 snapshot (session left there) or None (session state undefined)."""
        S = self.S
        target = want_x
        for _try in range(4):
            if abs(target - prev["x"]) > REACH + 6 or not bp.PXMIN <= target <= bp.PXMAX:
                return None
            S.restore(prev["snap"])
            Tc, Tn, d = self._walk(prev["T"], target=target)
            if d is not None or Tn != prev["T_next"]:
                self.say(f"   re-walk to x {target}: {'death' if d is not None else f'next room at T{Tn}, was T' + str(prev['T_next'])}")
                return None
            snap = S.snapshot()
            got = S.step(S.pad.fix(()))["x"]          # the entry x shows on the row after T = 0
            S.restore(snap)
            if got == want_x:
                return snap
            S.free(snap)
            target += want_x - got
        return None

    # -- the whole room ------------------------------------------------------------------------------------------
    def analyse(self, snap0, n_record):
        S = self.S
        tr, dead = record_room(S, snap0, n_record)
        ents = bp.entities_from_trace(tr)
        T_land = next((T for T in range(2, len(tr)) if tr[T]["jump"] == 0 and tr[T]["y"] >= 160), 40)
        air_y = {T: min(tr[T - 1]["y"], 152) - 40 for T in range(2, T_land + 1) if tr[T - 1]["jump"]}
        return dict(tr=tr, dead=dead, ents=ents, T_land=T_land, air_y=air_y, px=tr[1]["x"],
                    face=1 if tr[T_land]["aim"] >= 5 else 0,
                    plated=[e.eid for e in ents if e.kind == "core" and e.attr & 4])

    def solve(self, snap0, prev=None, n_record=440, t_max=430, hp_over=None, long=(600, 580), save_as=None):
        S = self.S
        R = RoomResult()
        R.plan_secs = 0.0
        R.lost = []
        t0 = time.time()
        A = self.analyse(snap0, n_record)
        ents, T_land, px, tr = A["ents"], A["T_land"], A["px"], A["tr"]
        R.ents = ents
        self.say(f"  room {tr[0]['screen']}: land T{T_land} px{px} passive death {A['dead']}; " + " ".join(map(repr, ents[:8])))
        forbid, noT, nb4, danger, deaths, kill_by = set(), set(), {}, [], set(), {}
        lost = set()
        jump_y = None
        for e in ents:
            if e.kind == "core" and not (e.attr & 4):
                x0, y0, _ = e.track[min(e.track)]
                if not any(bp.in_box(x0, yy, x0, y0, 5) for yy in (bp.STAND_Y, bp.CROUCH_Y)):
                    jump_y = self.jump_table(snap0, T_land)
                    self.say(f"   core at Y {y0} needs jump shots; jump lasts {len(jump_y)} frames")
                    break
        J = len(jump_y) if jump_y else 0
        hp_over = dict(hp_over or {})
        for eid in A["plated"]:
            hp_over[eid] = 23

        def plan(entry_masks, ctx=None):
            nonlocal n_record, t_max, A, ents, tr
            while True:
                tp = time.time()
                plans = bp.plan_room(ents, T_land + 1, entry_masks, A["air_y"], hp_over=hp_over, t_max=t_max,
                                     beam=self.beam, ntop=self.ntop, forbid=forbid, no_press=noT, not_before=nb4,
                                     plated=A["plated"], jump_y=jump_y, danger=danger, kill_by=kill_by, keep=self.keep,
                                     t0=2, lost=lost, **(ctx or {}))
                R.plan_secs += time.time() - tp
                if plans or ctx or not (long and t_max < long[1]):
                    return plans
                n_record, t_max = long
                A2 = self.analyse(snap0, n_record)
                A.update(tr=A2["tr"], ents=A2["ents"], dead=A2["dead"])
                ents, tr = A["ents"], A["tr"]
                R.ents = ents
                self.say(f"   no plan within the short horizon: recording {n_record} frames, planning to T{t_max}")

        def fixed_entry():
            m = bp.mask_range(px, px)
            return (0, m) if A["face"] else (m, 0)

        first = None
        if prev is not None and self.choose_entry:
            # plan with the entry x free (within reach of where the previous room ended), then make it so
            lo, hi = max(bp.PXMIN + 2, prev["x"] - REACH), min(bp.PXMAX - 4, prev["x"] + REACH)
            m = bp.mask_range(lo, hi) | bp.mask_range(px, px)
            plans = plan((m, m))
            if plans:
                ent = [(x, f) for f in (A["face"], 1 - A["face"]) for x in bp.mask_list(m)]
                dpad, pos, _ = bp.walk_rows(plans[0].presses, T_land + 1, ent, t0=2, jump_len=J, prefer=px)
                if dpad is not None:
                    want = pos["entry"][0]
                    self.say(f"   free-entry plan: finish {plans[0].finish} from x {want} (now {px})")
                    if want != px:
                        new0 = self.rewalk(prev, want)
                        if new0 is None:
                            self.say("   re-walk failed: staying with the entry as it is")
                            S.restore(snap0)
                        else:
                            snap0 = new0
                            A = self.analyse(snap0, n_record)
                            ents, T_land, px, tr = A["ents"], A["T_land"], A["px"], A["tr"]
                            R.ents = ents
                            if jump_y:
                                jump_y = self.jump_table(snap0, T_land)
                                J = len(jump_y)
                            first = plans[0]
                    else:
                        first = plans[0]
        R.snap0 = snap0
        S.restore(snap0)
        R.n_load = len(S.rows)
        if save_as:
            S.e.save(save_as)
        entry = (px, A["face"])
        plan_obj = info = None
        ctx = None              # prefix-preserving re-plan: dict(prefix, t_free, resume) + the d-pad rows to keep
        force = None
        n_deaths = 0
        for it in range(self.max_replans):
            was_first = first is not None
            if first is not None:
                plans, first = [first], None
            else:
                plans = plan(fixed_entry(), ctx)
                if not plans and ctx:
                    ctx = force = None          # what was played cannot be continued: plan the whole room again
                    continue
                if not plans and kill_by:
                    kill_by = {}                # the "shoot the soldiers early" demand cannot be met: drop it
                    continue
            if not plans:
                R.reason = "no plan"
                return R
            done = False
            plan_obj = plans[0]
            avoid = []
            last_death = None
            for _try in range(8):
                # a death while standing up to shoot: same plan, stand somewhere else for those presses
                st, info = self.execute(snap0, plan_obj, ents, T_land, entry, avoid=avoid, jump_len=J, force=force,
                                        lost=lost)
                if st != "death":
                    if st == "nopath" and avoid:
                        st, info = "death", last_death      # no other place to stand: a planner problem
                    break
                last_death = info
                avoid.append((info["T"] - 8, info["T"] + 2, info["x"] - 8, info["x"] + 8))
            self.say(f"   plan fin {plan_obj.finish}{' (rest from T' + str(ctx['t_free']) + ')' if ctx else ''}: {st} "
                     + ("" if st == "ok" else str({k: v for k, v in info.items() if k not in ("hits", "lag", "tail", "dpad", "path", "lost_seen")})))
            for T_ in info.get("lost_seen", ()):
                if T_ not in lost:
                    lost.add(T_)
                    R.lost.append(T_)
            unk = info.get("unk", [])
            for (uT, ui, ut, upos, _) in unk:
                # an enemy the passive recording did not have there (its path depends on where Bill is):
                # add it to the model as a soldier standing at that spot from now on
                ne = bp.Ent(len(ents), "soldier", ui, uT, 6, int(ut, 16))
                ne.attr, ne.hp0, ne.open = 0, 1, uT
                for tt in range(uT - 1, uT + 200):
                    ne.track[tt] = (upos[0], upos[1], True)
                ents.append(ne)
                for e2 in ents[:-1]:
                    if e2.etype == ne.etype and e2.kind == "soldier":
                        for tt in list(e2.track):
                            if tt >= uT - 40:
                                del e2.track[tt]
            t_keep = None           # rows before this one stay as they were played
            if st == "ok" and info["T_last_hit"] == plan_obj.finish:
                done = True
            elif was_first and st in ("nopath", "pos"):
                pass                # the free-entry plan does not fit the entry Bill really has: plan for that one
            elif st == "lost":
                noT.add(info["T"])
                t_keep = info["T"]
            elif st == "miss":
                for eid in set(info["want"]) - set(info["got"]):
                    forbid.add((info["T"], eid))
                    if ents[eid].kind == "soldier":
                        nb4[eid] = max(nb4.get(eid, 0), info["T"] + 6)
                if set(info["got"]) - set(info["want"]):
                    noT.add(info["press"])
                t_keep = info["press"]
            elif st == "extra":
                if not unk:
                    noT.add(info["press"])
                t_keep = info["press"]
            elif st == "death":
                n_deaths += 1
                if n_deaths >= MAX_DEATHS:
                    R.reason = f"{n_deaths} deaths"
                    R.replans = it
                    return R
                danger.append((info["T"] - 8, info["T"] + 1, bp.mask_range(info["x"] - 7, info["x"] + 7)))
                key = (info["T"], info["x"] // 4)
                lastp = max((p[0] for p in plan_obj.presses if p[0] <= info["T"]), default=None)
                if key in deaths and lastp is not None:
                    noT.add(lastp)
                deaths.add(key)
                if not kill_by and len(deaths) == 1:
                    kill_by = {e.eid: e.open + 45 for e in ents
                               if e.kind == "soldier" and e.open is not None and e.open + 45 < info["T"]}
            else:       # nopress / pos / nopath / wrong finish
                Tf = info.get("T", plan_obj.presses[-1][0])
                noT.add(Tf)
                if st in ("nopress", "pos"):
                    t_keep = Tf
            ctx = force = None
            if t_keep is not None:
                t_keep = max(3, t_keep - self.back)     # leave the planner a slot cycle before the failure to re-time
            if t_keep is not None and not unk and info.get("path") and t_keep > 3 and t_keep in info["path"]:
                ctx = dict(prefix=[p for p in plan_obj.presses if p[0] < t_keep], t_free=t_keep,
                           resume=info["path"][t_keep])
                force = {t: info["dpad"].get(t) for t in range(2, t_keep)}
            R.replans = it
            if done:
                break
        else:
            R.reason = "replans exhausted"
            return R
        R.plan = plan_obj
        R.T_last_hit = info["T_last_hit"]
        R.lag = info["lag"]
        tail = info.get("tail")
        w = self.walk(plan_obj.presses[-1][0] + bp.FLIGHT + 1, tail)
        if w is None:
            R.reason = "walk failed"
            return R
        R.T_cleared, R.T_next = w
        if tail is not None:
            # keep the tail snapshot for the next room's entry (s2.solve frees the session's other snapshots)
            if tail[0][0] in S.snaps:
                S.snaps.remove(tail[0][0])
            R.tail = dict(snap=tail[0], T=tail[1], x=tail[2], T_next=R.T_next)
        R.ok = True
        R.secs = time.time() - t0
        return R
