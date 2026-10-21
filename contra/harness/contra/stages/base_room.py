"""Closed-loop driver for one base room: record the room once without touching anything, plan the press schedule
on the abstract model (base_plan), execute it in the emulator, and re-plan with a new constraint whenever the
emulator disagrees. Then wait for the fence and walk into the next room.

T = frames since the room's enemies appeared (T = 0 is the frame `screen` changed / the stage's first frame + 1).
"""
from __future__ import annotations

import time

from . import base_plan as bp
from .base_common import Sess, bullets

SAFE_T = 2          # frames of Down released around a standing shot (rule: release >= 2)


class RoomResult:
    def __init__(self):
        self.ok = False
        self.reason = ""
        self.T_last_hit = None
        self.T_cleared = None
        self.T_next = None          # T (of this room) at which the next room's T = 0 falls
        self.plan = None
        self.lag = 0
        self.log = []
        self.replans = 0
        self.open = {}

    def __repr__(self):
        return (f"RoomResult(ok={self.ok} {self.reason} last_hit={self.T_last_hit} cleared={self.T_cleared} "
                f"next={self.T_next} lag={self.lag} replans={self.replans})")


def record_room(S: Sess, snap0, n=440, policy=None):
    """Play n frames from snap0 crouching (or policy(T, state) -> row), return the trace (index = T) and restore."""
    S.restore(snap0)
    tr = [S.s]
    dead = None
    T = 0
    while len(tr) < n:
        row = policy(T, S.s) if policy else ("Down",)
        s = S.step(S.pad.fix(row))
        if s["lagged"]:
            continue                      # a lag frame: no game logic ran; the trace is indexed by logic frames
        T += 1
        tr.append(s)
        if s["death"] & 1 and dead is None:
            dead = T
    S.restore(snap0)
    return tr, dead


def move_script(px, face, tx, tface):
    """[(button, frames)] to get from (px, face) to (tx, tface) with d-pad holds of at least 2 frames."""
    d = tx - px
    if d == 0 and face == tface:
        return []
    if tface == 0:
        if d >= 2:
            return [("Right", d)]
        m = max(2, 2 - d)
        return [("Left", m), ("Right", m + d)]
    if d <= -2:
        return [("Left", -d)]
    m = max(2, 2 + d)
    return [("Right", m), ("Left", m - d)]


def choose_path(presses, px0, face0, T0, avoid=()):
    """Pick (px, face) for every ground press from the plan's allowed masks so that each is reachable from the
    previous one with legal d-pad holds; fewest moved pixels. Airborne presses (pose 2) get None.
    Returns ([(px, face) | None], None) or (None, index of the press that cannot be reached)."""
    INF = 10 ** 9
    prev = {(px0, face0): (0, None)}
    layers = []
    idx = []
    tprev = T0
    for n, (T, k, mR, mL, hk, pose) in enumerate(presses):
        if pose == 2:
            continue
        dt = T - tprev
        cur = {}
        for f, m in ((0, mR), (1, mL)):
            for px in bp.mask_list(m):
                if pose == 0 and any(t0 <= T <= t1 and x0 <= px <= x1 for (t0, t1, x0, x1) in avoid):
                    continue                 # standing up there at that time was fatal in an earlier attempt
                bestc, bestp = INF, None
                for (qx, qf), (c, _) in prev.items():
                    need = sum(n2 for _, n2 in move_script(qx, qf, px, f))
                    if pose == 3 and need:
                        continue
                    if need <= dt - 2 and c + need < bestc:
                        bestc, bestp = c + need, (qx, qf)
                if bestp is not None:
                    cur[(px, f)] = (bestc, bestp)
        if not cur:
            return None, n
        layers.append(cur)
        idx.append(n)
        prev = cur
        tprev = T
    path = [None] * len(presses)
    if layers:
        end = min(prev.items(), key=lambda kv: kv[1][0])[0]
        for i in range(len(layers) - 1, -1, -1):
            path[idx[i]] = end
            end = layers[i][end][1]
    return path, None


class RoomSolver:
    def __init__(self, S: Sess, verbose=True, beam=12000, ntop=6, max_replans=20):
        self.S, self.verbose, self.beam, self.ntop, self.max_replans = S, verbose, beam, ntop, max_replans

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

    # -- one attempt at a plan -------------------------------------------------------------------------------
    def execute(self, snap0, plan, ents, T_land, crouch=True, up_wait=True, avoid=()):
        """Returns (status, info). status: 'ok' | 'nopath' | 'nopress' | 'miss' | 'extra' | 'death' | 'pos'."""
        S = self.S
        s = S.restore(snap0)
        presses = plan.presses
        cores = [e for e in ents if e.kind == "core"]
        # play to landing with nothing but the first move; find px there
        T = 0
        res = {"hits": [], "lag": 0}
        # we need the landing position before choosing the path: probe it
        probe = S.snapshot()
        while T < T_land:
            s = S.step(S.pad.fix(()))
            if not s["lagged"]:
                T += 1
        px_l, f_l = s["x"], (1 if s["aim"] >= 5 else 0)
        S.restore(probe)
        S.free(probe)
        T = 0
        path, bad = choose_path(presses, px_l, f_l, T_land - 1, avoid)
        if path is None:
            res["T"] = presses[bad][0]
            return "nopath", res
        script = []          # pending movement [(button, frames)]
        pi = 0               # next press index
        cur_px, cur_f = px_l, f_l
        pending = []         # (arrival T, expected hits, press index)
        T_end = presses[-1][0] + bp.FLIGHT + 1
        hp_prev = {e.eid: None for e in ents}
        last_hit_T = None
        first_ground = next((p for p in path if p is not None), None)
        script = move_script(cur_px, cur_f, *first_ground) if first_ground else []
        while T < T_end:
            row = []
            nextT = presses[pi][0] if pi < len(presses) else 10 ** 9
            pressing = pi < len(presses) and nextT == T + 1
            holding = pi > 0 and presses[pi - 1][0] == T      # second frame of the previous press
            if script and T >= T_land and not holding:
                b, n = script[0]
                row.append(b)
                script[0] = (b, n - 1)
                if n - 1 == 0:
                    script.pop(0)
            pose_now = presses[pi][5] if pressing else (presses[pi - 1][5] if holding else 0)
            if (pressing and presses[pi][1] == 0) or (holding and presses[pi - 1][1] == 0):
                row.append("A")
            elif pressing or holding:
                row.append("B")
                if pose_now == 1 and not [b for b in row if b in ("Left", "Right")]:
                    row.append("Down")
            elif crouch and not row and T >= T_land and not s["jump"] and (S.pad.len["Down"] or nextT - (T + 1) >= 2
                                                         or (pi < len(presses) and presses[pi][5] == 1)):
                row.append("Down")
            row = S.pad.fix(tuple(row))
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
            if pressing:
                (pT, k, mR, mL, hk, pose) = presses[pi]
                new = [b for b in bullets(s) if b[2] == 21]
                if k == 0:
                    if not s["jump"]:
                        res.update(T=T, why="no jump")
                        return "nopress", res
                    pi += 1
                    continue
                face = 1 if s["aim"] >= 5 else 0
                want = path[pi]
                if len(new) != k or (pose < 2 and new and new[0][5] != (156 if pose else 144)):
                    res.update(T=T, got=len(new), want=k, y=new[0][5] if new else None, x=s["x"], pad=s["pad"])
                    return "nopress", res
                if want is not None and (s["x"], face) != want:
                    okm = (mR if face == 0 else mL) >> (s["x"] - bp.PXMIN) & 1 if bp.PXMIN <= s["x"] <= bp.PXMAX else 0
                    if not okm:
                        res.update(T=T, x=s["x"], face=face, want=want)
                        return "pos", res
                if want is not None:
                    cur_px, cur_f = s["x"], face
                pending.append((T + bp.FLIGHT, hk, pi))
                pi += 1
                if pi < len(presses) and path[pi] is not None and want is not None:
                    script = move_script(cur_px, cur_f, *path[pi])
            if T == presses[-1][0] + 2:
                res["tail"] = (S.snapshot(), T)
            # arrivals
            if pending and pending[0][0] == T:
                _, hk, idx = pending.pop(0)
                got = []
                for i in range(16):
                    hb, ha = sp[f"eh{i}"], s[f"eh{i}"]
                    if sp[f"er{i}"] and sp[f"et{i}"] == s[f"et{i}"] and (
                            (0 < hb < 0xF0 and ha == hb - 1) or (s[f"et{i}"] == 0x14 and hb == 0 and ha in (4, 7))):
                        pos = (s[f"ex{i}"], s[f"ey{i}"])
                        m = [e for e in ents if e.etype == s[f"et{i}"] and T in e.track and e.track[T][:2] == pos]
                        got.append(m[0].eid if m else -1 - i)
                        if not m:
                            res.setdefault("unk", []).append((T, i, hex(s[f"et{i}"]), pos, [(e.eid, e.track[T][:2]) for e in ents if e.etype == s[f"et{i}"] and T in e.track]))
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

    # -- after the last hit: fence and walk ------------------------------------------------------------------
    def _walk(self, T, man=None):
        """Crouch until the room is cleared, then hold Up until the next room appears. man = optional dodge:
        ("jump", i) | ("Left"/"Right", i, n) | ("stand", i, n) applied at step i. Returns (T_cleared, T_next, None)
        or (None, None, step of death). The session is left on the next room's T = 0 frame."""
        S = self.S
        s = S.s
        scr = s["screen"]
        Tc = None
        for i in range(420):
            if s["cleared"] == 0:
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
        return None, None, 420

    def walk(self, T, tail=None):
        S = self.S
        Tc, Tn, d = self._walk(T)
        if d is None:
            return Tc, Tn
        if tail is None:
            return None
        snap, Tt = tail
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

    # -- the whole room ------------------------------------------------------------------------------------------
    def solve(self, snap0, n_record=440, t_max=430, hp_over=None, long=(560, 540)):
        S = self.S
        R = RoomResult()
        t0 = time.time()
        tr, dead = record_room(S, snap0, n_record)
        ents = bp.entities_from_trace(tr)
        R.ents = ents
        T_land = next((T for T in range(1, len(tr)) if tr[T]["jump"] == 0 and tr[T]["y"] >= 160), 40)
        px = tr[T_land]["x"]
        self.say(f"  room {tr[0]['screen']}: land T{T_land} px{px} passive death {dead}; " + " ".join(map(repr, ents[:8])))
        forbid = set()
        noT = set()
        nb4 = {}
        danger = []
        deaths = set()
        kill_by = {}
        air = {T: (tr[T - 1]["x"], min(tr[T - 1]["y"], 152) - 40) for T in range(2, T_land) if tr[T - 1]["jump"]}
        plated = [e.eid for e in ents if e.kind == "core" and e.attr & 4]
        jump_y = None
        for e in ents:
            if e.kind == "core" and not (e.attr & 4):
                x0, y0, _ = e.track[min(e.track)]
                if not any(bp.in_box(x0, yy, x0, y0, 5) for yy in (bp.STAND_Y, bp.CROUCH_Y)):
                    jump_y = self.jump_table(snap0, T_land)
                    self.say(f"   core at Y {y0} needs jump shots; jump lasts {len(jump_y)} frames")
                    break
        hp_over = dict(hp_over or {})
        for eid in plated:
            hp_over[eid] = 23
        for it in range(self.max_replans):
            plans = bp.plan_room(ents, T_land + 1, px, px, hp_over=hp_over,
                                 t_max=t_max, beam=self.beam, ntop=self.ntop, forbid=forbid, no_press=noT, not_before=nb4, air=air, plated=plated, jump_y=jump_y, danger=danger, kill_by=kill_by,
                                 face0=1 if tr[T_land]["aim"] >= 5 else 0)
            if not plans and kill_by:
                kill_by = {}                # the "shoot the soldiers early" demand cannot be met: drop it
                continue
            if not plans and long and t_max < long[1]:
                n_record, t_max = long
                tr, dead = record_room(S, snap0, n_record)
                ents = bp.entities_from_trace(tr)
                R.ents = ents
                self.say(f"   no plan within the short horizon: recording {n_record} frames, planning to T{t_max}")
                continue
            if not plans:
                R.reason = "no plan"
                return R
            done = False
            for plan in plans[:1]:
                avoid = []
                for _try in range(8):
                    # a death while standing up to shoot: same plan, stand somewhere else for those presses
                    st, info = self.execute(snap0, plan, ents, T_land, avoid=avoid)
                    if st != "death":
                        if st == "nopath" and avoid:
                            st, info = "death", last_death      # no other place to stand: a planner problem
                        break
                    last_death = info
                    avoid.append((info["T"] - 8, info["T"] + 2, info["x"] - 8, info["x"] + 8))
                self.say(f"   plan fin {plan.finish}: {st} " + ("" if st == "ok" else str({k: v for k, v in info.items() if k not in ("hits", "lag")})))
                for (uT, ui, ut, upos, _) in info.get("unk", []):
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
                if st == "ok" and info["T_last_hit"] == plan.finish:
                    done = True
                elif st == "miss":
                    for eid in set(info["want"]) - set(info["got"]):
                        forbid.add((info["T"], eid))
                        if ents[eid].kind == "soldier":
                            nb4[eid] = max(nb4.get(eid, 0), info["T"] + 6)
                    if set(info["got"]) - set(info["want"]):
                        noT.add(info["press"])
                elif st == "extra":
                    if not info.get("unk"):
                        noT.add(info["press"])
                elif st == "death":
                    # standing there at that time was fatal: keep Bill away from that spot around that time;
                    # if the same death comes back, also give up the press before it
                    danger.append((info["T"] - 8, info["T"] + 1, bp.mask_range(info["x"] - 7, info["x"] + 7)))
                    key = (info["T"], info["x"] // 4)
                    lastp = max((p[0] for p in plan.presses if p[0] <= info["T"]), default=None)
                    if key in deaths and lastp is not None:
                        noT.add(lastp)
                    deaths.add(key)
                    if not kill_by and len(deaths) == 1:
                        # first death in this room: demand that every soldier on the wall by then is shot within
                        # 45 frames of appearing (their bullets come straight down where Bill has to stand)
                        kill_by = {e.eid: e.open + 45 for e in ents
                                   if e.kind == "soldier" and e.open is not None and e.open + 45 < info["T"]}
                else:       # nopress / pos / nopath / wrong finish
                    noT.add(info.get("T", plan.presses[-1][0]))
            R.replans = it
            if done:
                break
        else:
            R.reason = "replans exhausted"
            return R
        R.plan = plan
        R.T_last_hit = info["T_last_hit"]
        R.lag = info["lag"]
        w = self.walk(plan.presses[-1][0] + bp.FLIGHT + 1, info.get("tail"))
        if w is None:
            R.reason = "walk failed"
            return R
        R.T_cleared, R.T_next = w
        R.ok = True
        R.secs = time.time() - t0
        return R
