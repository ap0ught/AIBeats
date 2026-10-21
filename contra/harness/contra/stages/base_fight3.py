"""Third pass (2026-10-12): the base boss executor with a cheap repair for lost controller reads.

BossFight3 = base_bfight.BossFight with one change in run(): when the game does not read the pad on a frame on
which the buttons were to change, the plan is first repaired by "repeat the previous frame's buttons now, play the
rest one frame late up to some frame k, and drop frame k" (tried for every k on the exact model, about half a
second); the result has the old plan's length, so the lost read costs nothing. Only if no k works does it go on as
before (shift the whole plan by a frame, else plan the rest again) - without the "guided" quick search, which never
produced an accepted plan in six logged cases and took 2 to 13 minutes each time.

Why a separate module: a full re-plan of the plating phase is 12-17 minutes of the six-process portfolio, and the
second pass's runs needed one or two per fight (L2: 936 + 193 + 1035 + 112 + 755 s of planning for one fight).
The planner workers still import base_bfight (plan_job); nothing they use is changed here.

Third pass, part 2 (2026-10-16): PROBING. Which frames the game does not read depends only on the inputs played, so a
plan played open-loop on the emulator from the current state shows exactly which of its button changes will be lost
and on which row the phase really ends. plan() therefore asks the whole portfolio (plus the Eye's prepared-jump
line) as before, then plays the candidates on the emulator in order of their model length (state saved and restored,
nothing kept) and takes the one that ends the phase first ON THE EMULATOR. The lost reads of the chosen plan that the
probe saw are then expected by run(): it does not take those frames back (the model is stepped with the buttons the
game saw, as for any frame). Costs about a second per candidate probed.
"""
from __future__ import annotations

import time

from . import base_bfight as bf
from . import base_bplan as bp
from . import base_bsim as bs
from .base_common import Sess

E_SLOT, E_X = bs.E_SLOT, bs.E_X


def repair_lost(sim, pad0, prev_act, rest, goal, hold_at=()):
    """rest = the plan from the frame that was not read. Returns (acts, k) with acts = [prev_act] + rest[:k] +
    rest[k+1:] reaching the goal on the model (same length as rest), for the smallest such k, or None.
    hold_at = indices (into the result) of frames that are known not to be read: no change of buttons there."""
    n = len(rest)
    for k in range(n):
        cand = [prev_act] + rest[:k] + rest[k + 1:]
        if any(0 < d < len(cand) and cand[d] != cand[d - 1] for d in hold_at):
            continue
        out = bf.model_outcome(sim, pad0, cand, goal)
        if out is not None:
            return cand[:out], k
    return None


PROBE = True           # play the candidate plans on the emulator before choosing one (see the module text)
PROBE_SLACK = 8        # probe candidates whose model length is at most this much above the shortest
PROBE_MAX = 8


class BossFight3(bf.BossFight):
    tol_rows = frozenset()      # absolute row indices of lost reads the current plan was probed with (expected)

    def probe(self, acts, phase, need):
        """Play acts open-loop from the current state (restored afterwards). Returns (rows to the phase's goal or
        None, [absolute row indices on which a button change was not read])."""
        S = self.S
        snap = S.snapshot()
        drops = []
        res = None
        n = i = 0
        prev = S.rows[-1] if S.rows else ()
        try:
            while i < len(acts) and n < len(acts) + 40:
                row = bp.act_row(acts[i])
                k = len(S.rows)
                s = S.step(row)
                n += 1
                if s["lagged"]:
                    continue
                if s["pad"] != self.mask(row) and tuple(row) != tuple(prev):
                    drops.append(k)
                prev = row
                i += 1
                if (s["death"] & 1) or (s["pstate"] != 1 and not s["bossdef"]):
                    break
                if (phase == "A" and s["plates"] >= need) or (phase == "B" and s["bossdef"]):
                    res = n
                    break
        except ValueError:
            res = None
        finally:
            S.restore(snap)
            S.free(snap)
        return res, drops

    def plan(self, m, opts=None, quick=False):
        """base_bfight.BossFight.plan, keeping every candidate; the candidates are then probed on the emulator."""
        S = self.S
        sim = bs.Sim.from_ram(m)
        phase = bf.phase_of(sim)
        pad = bp.pad_from_rows(S.rows)
        prev_act = bp.act_of_row(S.rows[-1]) if S.rows else 0
        t0 = time.time()
        n = len(S.rows)
        repeat = sorted(d - n for d in self.known if d >= n)
        opts = dict(opts or {})
        opts.setdefault("hz_margin", self.hz_margin)
        kc = (phase == "A" and self.kill_cannon and bf.final_type(sim) == bs.T_HELMET
              and any(e[0] == bs.T_CANNON and e[bf.E_R] <= 3 for e in sim.en))
        if kc:
            opts["kill_cannon"] = True
        cfgs = self.portfolio or bf.portfolio_for(sim, kc)
        if quick:
            cfgs = cfgs[:3]
        best, res = bf.plan_portfolio(self.pool, m, pad, prev_act, cfgs, repeat=repeat, opts=opts)
        if best is None and kc and not quick:
            self.say("   no plan that destroys the cannon: planning without it")
            self.kill_cannon = False
            opts.pop("kill_cannon")
            best, res = bf.plan_portfolio(self.pool, m, pad, prev_act, self.portfolio or bf.portfolio_for(sim),
                                          repeat=repeat, opts=opts)
        summ = [(r["cfg"], r["n"], r["stats"]["secs"]) for r in res]
        cands = sorted(((r["cost"], r["n"], r["acts"], str(r["cfg"])) for r in res if r["acts"] is not None),
                       key=lambda c: (c[0], c[1]))
        burst = None
        if phase == "B" and not quick and "guide" not in opts and bf.final_type(sim) == bs.T_EYE and self.eye_burst:
            try:
                burst = self.burst_plan(sim, pad, prev_act, repeat, opts)
            except Exception as ex:  # noqa: BLE001
                self.say(f"   eye burst plan failed: {ex!r}")
            if burst is not None:
                self.say(f"   prepared-jump plan: {len(burst)} frames (portfolio {cands[0][1] if cands else None})")
                cands.append((len(burst), len(burst), burst, "prepared jump"))
                cands.sort(key=lambda c: (c[0], c[1]))
        seen_p, uniq = set(), []
        for c in cands:
            key = tuple(c[2])
            if key not in seen_p:
                seen_p.add(key)
                uniq.append(c)
        cands = uniq
        chosen, probes = None, []
        if cands and PROBE and not quick:
            n_min = min(c[1] for c in cands)
            for c in sorted(cands, key=lambda c: (c[1], c[0]))[:PROBE_MAX]:
                if c[1] > n_min + PROBE_SLACK or (chosen is not None and c[1] >= chosen[0]):
                    break
                got, drops = self.probe(c[2], phase, sim.need)
                probes.append((c[3], c[1], got, [d - n for d in drops]))
                if got is not None and (chosen is None or got < chosen[0]):
                    chosen = (got, c, drops)
            if probes:
                self.say(f"   probed on the emulator (setting, model frames, emulator frames, lost changes): {probes}")
        if chosen is not None:
            acts, self.tol_rows = chosen[1][2], frozenset(chosen[2])
            n_best = chosen[1][1]
        elif cands:
            acts, self.tol_rows = cands[0][2], frozenset()
            n_best = cands[0][1]
        else:
            acts, self.tol_rows, n_best = None, frozenset(), None
        self.info["plans"].append({"at": len(S.rows) - self.n0, "phase": phase, "repeat": list(repeat),
                                   "best": n_best, "all": summ, "secs": round(time.time() - t0),
                                   "guided": bool(quick), "burst": len(burst) if burst else None,
                                   "probes": probes, "emu": chosen[0] if chosen else None})
        self.say(f"   plan {phase} at boss row {len(S.rows) - self.n0}: best {n_best} frames"
                 f"{' (emulator ' + str(chosen[0]) + ')' if chosen else ''}; all {[r[1] for r in summ]} "
                 f"({round(time.time() - t0)} s)")
        return acts

    def run(self):
        """From the boss room's first frame to the frame BOSS_DEFEATED_FLAG is set. Returns the info dict.
        (base_bfight.BossFight.run with the lost-read repair; see the module text.)"""
        S = self.S
        t0 = time.time()
        self.n0 = n0 = len(S.rows)
        info = self.info
        info["repairs"] = []
        for _ in range(40):
            s = S.step(S.pad.fix(()))
            if not s["lagged"]:
                break
            info["lag"] += 1
        m = self.ram()
        sim = bs.Sim.from_ram(m)
        info["start"] = {"row": len(S.rows) - n0, "fc": m[0x1A], "rng": m[0x34], "x": sim.px,
                         "parts": [(e[0], e[E_SLOT], e[E_X], e[bs.E_Y]) for e in sim.en]}
        acts = self.plan(m)
        if acts is None:
            info.update(ok=False, why="no plan", frames=len(S.rows) - n0)
            return info
        i = 0
        goal_a = lambda s: s.plates >= s.need            # noqa: E731
        goal_b = lambda s: s.bossdef                     # noqa: E731
        phase = "A"
        hp_prev = sim.hp_left()
        fails = 0
        CKPT = 10
        while True:
            if i < len(acts) and (len(S.rows) - n0) % CKPT == 0 and (not self.ckpts or self.ckpts[-1][2] != len(S.rows)):
                self.ckpts.append((S.snapshot(), phase, len(S.rows)))
                if len(self.ckpts) > 8:
                    S.free(self.ckpts.pop(0)[0])
            if i >= len(acts):
                acts = self.plan(self.ram())
                i = 0
                fails += 1
                if acts is None or fails > 6:
                    info.update(ok=False, why="plan exhausted", frames=len(S.rows) - n0)
                    return info
            act = acts[i]
            row = bp.act_row(act)
            prev_row = S.rows[-1] if S.rows else ()
            snap = S.snapshot() if tuple(row) != tuple(prev_row) else None
            s = S.step(row)
            if s["lagged"]:
                info["lag"] += 1
                S.free(snap) if snap else None
                acts = acts[:i] + [act] + acts[i:]
                i += 1
                continue
            m = self.ram()
            seen = m[0xF1]
            if seen != self.mask(row):
                info["drops"].append((len(S.rows) - n0, seen, self.mask(row)))
                if snap is not None and len(S.rows) - 1 in self.tol_rows:
                    # probed: this plan was chosen knowing that this change is not read here
                    info["expected_drops"] = info.get("expected_drops", 0) + 1
                    S.free(snap)
                    snap = None
                if snap is not None:
                    self.tol_rows = frozenset()         # the plan changes from here
                    S.restore(snap)
                    S.free(snap)
                    self.known.add(len(S.rows))
                    m0 = self.ram()
                    sim = bs.Sim.from_ram(m0)
                    pad0 = bp.pad_from_rows(S.rows)
                    goal = goal_a if phase == "A" else goal_b
                    prev_act = bp.act_of_row(prev_row)
                    old = len(acts) - i
                    bs.HZ_MARGIN = 0
                    nrow = len(S.rows)
                    rep = repair_lost(sim, pad0, prev_act, acts[i:], goal,
                                      hold_at=[d - nrow for d in self.known if d > nrow])
                    if rep is not None:
                        self.say(f"   pad not read at boss row {nrow - n0 + 1}: plan needed {old} more frames; repaired "
                                 f"(rest one frame late up to frame {rep[1]}, that frame dropped): {len(rep[0])} frames")
                        info["repairs"].append((nrow - n0 + 1, rep[1], old, len(rep[0])))
                        acts, i = rep[0], 0
                        continue
                    shifted = [prev_act] + acts[i:]
                    sh = bf.model_outcome(sim, pad0, shifted, goal)
                    self.say(f"   pad not read at boss row {nrow - n0 + 1}: plan needed {old} more frames, no repair, "
                             f"shifted plan gives {sh}")
                    if sh is not None and sh <= old + 1:
                        acts, i = shifted, 0
                        continue
                    new = self.plan(m0)
                    if new is not None and (sh is None or len(new) < sh):
                        acts, i = new, 0
                        continue
                    if sh is not None:
                        acts, i = shifted, 0
                        continue
                    new = None
                    while self.ckpts and new is None:
                        ck, ph, _ = self.ckpts.pop()
                        S.restore(ck)
                        S.free(ck)
                        info["backups"] += 1
                        m0 = self.ram()
                        self.say(f"   going back to boss row {len(S.rows) - n0}")
                        new = self.plan(m0)
                    if new is None:
                        info.update(ok=False, why="no plan after a lost pad read", frames=len(S.rows) - n0)
                        return info
                    sim = bs.Sim.from_ram(m0)
                    hp_prev = sim.hp_left()
                    acts, i = new, 0
                    continue
            if snap is not None:
                S.free(snap)
            dpad, a_new, b_new = seen & 0x0F, seen & m[0xF5] & 0x80, seen & m[0xF5] & 0x40
            sim.step(dpad, 1 if a_new else 0, 1 if b_new else 0)
            i += 1
            if m[0x90] != 1 and not m[0x3B]:
                info.update(ok=False, why=f"player state {m[0x90]} at boss row {len(S.rows) - n0}", frames=len(S.rows) - n0)
                return info
            if not bf.model_matches(sim, m):
                info["resyncs"] += 1
                sim = bs.Sim.from_ram(m)
                goal = goal_a if phase == "A" else goal_b
                if not goal(sim):
                    left = bf.model_outcome(sim, bp.pad_from_rows(S.rows), acts[i:], goal)
                    self.say(f"   model re-loaded from RAM at boss row {len(S.rows) - n0}; rest of the plan: "
                             f"{left} frames (was {len(acts) - i})")
                    if left is None or left > len(acts) - i:
                        new = self.plan(m)
                        if new is not None and (left is None or len(new) < left):
                            acts, i = new, 0
                        elif left is None:
                            info.update(ok=False, why="no plan after a model mismatch", frames=len(S.rows) - n0)
                            return info
            hp = sim.hp_left()
            if hp != hp_prev:
                info["events"].append((len(S.rows) - n0, hp))
                hp_prev = hp
            if phase == "A" and m[0x87] >= sim.need:
                info["plates_done"] = len(S.rows) - n0
                self.say(f"   platings gone at boss row {info['plates_done']} (Bill at x {sim.px}, {'air' if sim.jump else 'ground'})")
                phase = "B"
                for ck in self.ckpts:
                    S.free(ck[0])
                self.ckpts = []
                acts = self.plan(m)
                i = 0
                if acts is None:
                    info.update(ok=False, why="no plan for the final part", frames=len(S.rows) - n0)
                    return info
                continue
            if m[0x3B]:
                break
        info.update(ok=True, frames=len(S.rows) - n0, secs=round(time.time() - t0), end_x=m[0x334],
                    end_jump=1 if m[0xA0] else 0)
        return info


def solve_boss(S: Sess, procs=None, verbose=True, **_):
    """As base_bfight.solve_boss, with BossFight3."""
    import multiprocessing as mp
    import os
    procs = procs or int(os.environ.get("BASE_BOSS_PROCS", "6"))
    n0 = len(S.rows)
    if procs <= 1:
        info = BossFight3(S, pool=None, verbose=verbose).run()
    else:
        with mp.get_context("spawn").Pool(procs) as pool:
            info = BossFight3(S, pool=pool, verbose=verbose).run()
    info["frames"] = len(S.rows) - n0
    return info
