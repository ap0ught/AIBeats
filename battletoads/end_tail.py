"""end_tail.py - the correct ending of a run, as short as the game allows (track END, 2026-10-09).

The run ends at the cut to Professor T. Bird = the SECOND level-byte 13 -> 254 change, not at the first (the Dark Queen's
speech). This tool takes a Dark Queen fight, finds its last hit, and appends the legal tail:

    python end_tail.py <L13 segment> <out segment>              plain tail: nothing, one A press on the first frame the speech
                                                                screen accepts it, nothing
    python end_tail.py <L13 segment> <out segment> --steer 600  the same, but first re-roll the ending's dice with single
                                                                Select presses (600 s search budget)
    ... --route up14 --state cap14_f46000 --frame 46000         build on a replay-exact state of a verified route instead of
                                                                the segment's own bookmark (the tail's dice depend on the
                                                                exact machine state; a bookmark made inside a tool can differ)

Writes logs/pbeam_<out>.json = the fight's inputs up to the last hit + the tail up to the T. Bird cut (+ 30 idle frames),
with an "end" block: last_hit, queen_speech_cut, back, tbird_cut (input indices inside the segment), and prints them.
ALWAYS a fresh <out> name. Verify the route afterwards with assemble.py (it now reports the T. Bird cut).

What can and cannot be shortened (model and numbers: end_model.py, knowledge/end_timing.md):
  * the speech screen polls the pad 9..12 frames after the cut (dice); a NEW press of A/B/Select on that frame returns to
    the tower on the same frame. One frame is enough; a press held from earlier is not new and does nothing. Never Start.
  * back on the tower the game waits for the Queen's whirl timer to reach zero before it cuts to T. Bird: 1..256 frames.
    The timer's last reloads are dice thrown while she rises (heights 0..127); a Select press (it does nothing else in play)
    on any earlier frame re-rolls them. --steer searches presses so the timer parks as early as it can.
  * the toad must not stand within ~25 px of x 128 when she rises: she hits it three times (27 frozen frames, dead toad).

Import use (the fight search):  from end_model import predict   (RAM at the last hit -> frames to the T. Bird cut)
                                from end_tail import Ending      (run / steer the tail on a live emulator)
"""
from __future__ import annotations

import json
import random
import sys
import time

import end_model as M
from toads.emulator import BizHawk, LOGS_DIR

FIX = LOGS_DIR / "fix"
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
SETS = (("Select",), ("Down",), ("Down", "Select"), ("Up",), ("Up", "Select"))   # single-frame presses used to re-roll dice
LADDER = 24


def fmt(b) -> str:
    return "+".join(b)


class Ending:
    """Drives the ending on a live emulator that has just executed the last-hit frame (Queen id 0x46)."""

    def __init__(self, e: BizHawk, log=print):
        self.e = e
        self.log = log
        self.base = e.msave()
        self.m0 = e.ram_all()
        self.s = M.queen_slot(self.m0)
        assert self.s is not None and self.m0[M.T_ID + self.s] == M.DEAD, "not on the last-hit frame (Queen id is not 0x46)"
        self.hit = M.read_hit(self.m0, self.s)
        self.sched: dict[int, tuple] = {}            # offset (frames after the last hit, 1 = next frame) -> buttons
        self.frames_run = 0
        self.resp = self.h0 = self.n1 = None

    # -- emulator helpers ---------------------------------------------------
    def _run(self, a: int, b: int, sched: dict) -> None:
        """advance from offset a to offset b under sched"""
        e = self.e
        f = a
        keys = sorted(o for o in sched if a < o <= b)
        for o in keys:
            if o - 1 > f:
                e.step((), o - 1 - f)
            e.step(sched[o], 1)
            f = o
        if b > f:
            e.step((), b - f)
        self.frames_run += b - a

    def _q(self):
        m = self.e.ram(0x3C0, 0x1E8)
        g = lambda a: m[a - 0x3C0]
        s = self.s
        return {"id": g(M.T_ID + s), "A": g(M.T_TMR + s), "d": M.s8(g(M.T_DIR + s)), "th": g(M.T_ANG + s),
                "h": g(M.T_HLO + s) + 256 * M.s8(g(M.T_HHI + s)), "toad_x": g(0x3FD), "toad_h": g(0x439), "toad_hp": g(0x51A)}

    def F(self, k: int) -> int:
        """offset of rise frame k"""
        return self.resp + 207 + k

    # -- 1. the flight: find the respawn, move the toad out of the Queen's column -----------------------------
    def measure(self) -> None:
        e = self.e
        e.mload(self.base)
        off = 0
        while off < 400:
            e.step(self.sched.get(off + 1, ()), 1)
            off += 1
            if e.byte(M.T_ID + self.s) == M.QID:
                break
        else:
            raise RuntimeError("the Queen never came back (no respawn within 400 frames)")
        self.resp = off
        q = self._q()
        self.h0 = q["h"]
        tx = q["toad_x"]
        self.log(f"last hit: timer {self.hit['a']} angle {self.hit['theta']} step {self.hit['d']} Queen height {self.hit['h']}; "
                 f"flight {self.resp} frames, respawn height {self.h0}, toad at x {tx} h {q['toad_h']}")
        if 96 <= tx <= 160:                           # she rises at x 128 and would hit the toad: walk away, then re-measure
            away = "Left" if tx < 128 else "Right"
            for o in range(self.resp + 1, self.resp + 61):
                self.sched[o] = (away,)
            e.mload(self.base)
            self._run(0, self.resp + 90, self.sched)
            q = self._q()
            self.log(f"toad was in the Queen's column: walking {away} for 60 frames -> x {q['toad_x']} h {q['toad_h']}")
            if 96 <= q["toad_x"] <= 160:
                self.log("WARNING: the toad is still in the column; expect three hits (+27 frames)")
        e.mload(self.base)
        self._run(0, self.resp + 208, self.sched)
        t = e.byte(0x0B)
        self.n1 = 171 if t % 2 == 0 else 172
        self.cut1 = self.resp + 207 + self.n1 + 122
        self.lo = M.k128(self.h0)

    # -- 2. steer the whirl timer ----------------------------------------------------------------------------
    def _outcome(self, draws):
        """model: (final wait if decided, None) or (None, best wait still reachable)"""
        h = self.hit
        r = M.simulate(h["a"], h["theta"], h["d"], self.h0, self.n1, draws=draws)
        if not r["open"]:
            return r["wait"], None, r
        w, _ = M.best_draws(h["a"], h["theta"], h["d"], self.h0, self.n1, prefix=draws)
        return None, w, r

    def steer(self, budget_s: float = 600.0, tol: int = 0, seed: int = 1) -> dict:
        """Search single-frame presses that make the timer park as early as possible. Returns the best found."""
        h = self.hit
        rng = random.Random(seed)
        t0 = time.time()
        floor_wait = self.lo + 84 - self.n1
        w0, pot0, r0 = self._outcome([])
        self.best = {"wait": w0 if w0 is not None else M.BIG, "sched": dict(self.sched), "draws": []}
        if w0 is not None:
            self.log(f"no dice in this ending: the timer is decided at the last hit, final wait {w0} frames (floor {floor_wait})")
            return self.best
        self.log(f"model: floor wait {floor_wait}, best reachable {pot0}; first dice on rise frame {r0['need'][0]} (offset {self.F(r0['need'][0])})")
        # plain outcome first (no presses) so there is always a complete answer
        self._plain_outcome()
        nodes = [(pot0, 0, dict(self.sched), [], self.base, 0)]       # (potential, depth, sched, draws, state, state offset)
        tried = 0
        while nodes and time.time() - t0 < budget_s and self.best["wait"] > floor_wait + tol:
            nodes.sort(key=lambda n: (n[0], -n[1]))
            pot, depth, sched, draws, state, soff = nodes.pop(0)
            if pot >= self.best["wait"]:
                continue
            r = M.simulate(h["a"], h["theta"], h["d"], self.h0, self.n1, draws=draws)
            k0, th0 = r["need"]
            F = self.F(k0)
            # ladder of states along this node's path
            self.e.mload(state)
            ladder = {soff: state}
            o = soff
            while o + LADDER < F - 1:
                self._run(o, o + LADDER, sched)
                o += LADDER
                ladder[o] = self.e.msave()
            offs = sorted(ladder)
            first = max(soff + 1, 12 if depth == 0 else soff + 1)
            cands = [(j, b) for j in range(F - 1, first - 1, -1) for b in SETS if j not in sched]
            pairs = []
            span = list(range(first, F))
            for _ in range(4000):
                if len(span) < 2:
                    break
                j1, j2 = sorted(rng.sample(span, 2))
                if j1 in sched or j2 in sched:
                    continue
                pairs.append(((j1, rng.choice(SETS)), (j2, rng.choice(SETS))))
            seen = set()
            opened = []
            n_here = 0
            for cand in cands + pairs:
                if time.time() - t0 > budget_s or self.best["wait"] <= floor_wait + tol:
                    break
                presses = [cand] if isinstance(cand[0], int) else list(cand)
                sc = dict(sched)
                for j, b in presses:
                    sc[j] = b
                j0 = min(j for j, _ in presses)
                lo_off = max(x for x in offs if x <= j0 - 1)
                self.e.mload(ladder[lo_off])
                self._run(lo_off, F, sc)
                q = self._q()
                tried += 1
                n_here += 1
                if q["th"] != th0:
                    self.log(f"  (angle {q['th']} is not the model's {th0} at offset {F}: skipped)")
                    continue
                dr = draws + [(q["A"], q["d"])]
                key = (q["A"], q["d"])
                w, p, _ = self._outcome(dr)
                if w is not None:
                    if w < self.best["wait"]:
                        self.best = {"wait": w, "sched": sc, "draws": dr}
                        self.log(f"  [{time.time() - t0:5.0f}s, {tried} tries] final wait {w} (floor {floor_wait}) with draws {dr}, "
                                 f"presses {sorted((j, fmt(b)) for j, b in sc.items() if j not in self.sched)}")
                elif key not in seen and p < self.best["wait"]:
                    opened.append((p, depth + 1, sc, dr, F))
                seen.add(key)
                if len(opened) >= 60 and n_here >= 300 and w is None:
                    break                              # enough second-level openings; the pairs are for last-level dice
            for st in [v for k, v in ladder.items() if k != soff]:
                self.e.mfree(st)
            # open the most promising next-level nodes (each needs its own state at its dice frame)
            opened.sort(key=lambda n: (n[0], -(n[3][-1][0])))
            for p, dp, sc, dr, Fo in opened[:10]:
                self.e.mload(state)
                self._run(soff, Fo, sc)
                nodes.append((p, dp, sc, dr, self.e.msave(), Fo))
            self.log(f"  depth {depth}: {n_here} tries at dice frame {F}, {len(opened)} openings, best wait so far {self.best['wait']}")
        self.sched = dict(self.best["sched"])
        self.log(f"steer: {tried} tries, {self.frames_run} frames emulated, {time.time() - t0:.0f} s -> final wait {self.best['wait']} "
                 f"(floor {floor_wait}), draws {self.best['draws']}")
        return self.best

    def _plain_outcome(self) -> None:
        """what the dice give with the current schedule and nothing else (reads the timer after each reload)"""
        h = self.hit
        draws = []
        self.e.mload(self.base)
        off = 0
        for _ in range(4):
            r = M.simulate(h["a"], h["theta"], h["d"], self.h0, self.n1, draws=draws)
            if not r["open"]:
                self.best = {"wait": r["wait"], "sched": dict(self.sched), "draws": draws}
                self.log(f"  unsteered: draws {draws} -> final wait {r['wait']}")
                return
            F = self.F(r["need"][0])
            self._run(off, F, self.sched)
            off = F
            q = self._q()
            draws = draws + [(q["A"], q["d"])]

    # -- 3. the speech: find a press that makes the screen poll on its 9th frame, then the single A press ----------
    def _to_cut1(self, sched, state=None, soff=0):
        """run to the first cut; returns its offset (the frame the level byte reads 254)"""
        e = self.e
        e.mload(state if state is not None else self.base)
        target = self.cut1
        if target - 3 > soff:
            self._run(soff, target - 3, sched)
            off = target - 3
        else:
            off = soff
        while off < target + 400:
            e.step(sched.get(off + 1, ()), 1)
            off += 1
            self.frames_run += 1
            if e.byte(0x10) == 254:
                return off
        raise RuntimeError("no cut to the Queen's speech")

    def _speech(self, sched, state=None, soff=0):
        """Run to the cut to the Queen's speech and through it. Returns (cut1 offset, skip, lag):
        skip = frames from the cut to the first frame on which the speech screen takes a press (measured with a NEW press on
        every frame: A, B, A, ...), lag = frames from the return to the tower (one A press on that frame, nothing else) to
        the first frame the level timer $0B runs again (14 or 15: the reload takes a variable number of frames).
        The T. Bird cut comes exactly 340 + (whirl timer) frames after that."""
        e = self.e
        cut1 = self._to_cut1(sched, state, soff)
        st = e.msave()
        skip = None
        for j in range(1, 40):
            e.step(("A",) if j % 2 else ("B",), 1)
            if e.byte(0x10) == 13:
                skip = j
                break
        self.frames_run += 40
        if skip is None:
            e.mfree(st)
            raise RuntimeError("the speech was not skipped within 40 frames")
        lag = None
        for sk in (skip, skip + 1, skip + 2):
            e.mload(st)
            if sk > 1:
                e.step((), sk - 1)
            e.step(("A",), 1)
            if e.byte(0x10) != 13:
                continue
            for n in range(1, 60):
                e.step((), 1)
                if e.byte(0x0B) != 0:
                    lag = n
                    break
            skip = sk
            break
        self.frames_run += 60
        e.mfree(st)
        if lag is None:
            raise RuntimeError("a single A press did not skip the speech")
        return cut1, skip, lag

    def finish(self, steer_skip: bool = True) -> dict:
        e = self.e
        sched = dict(self.sched)
        cut1, skip, lag = self._speech(sched)
        if cut1 != self.cut1:
            self.log(f"NOTE: first cut at offset {cut1}, the model said {self.cut1} (the toad was hit? lag?)")
            self.cut1 = cut1
        self.log(f"Queen's speech: cut at offset {cut1}; the screen takes a press {skip} frames later, the tower is back "
                 f"{lag} frames after that ({skip + lag} in all; the least seen is 9 + 14 = 23)")
        if steer_skip and skip + lag > M.SKIP_MIN + M.LAG_MIN:
            s0 = max(0, cut1 - 70)
            e.mload(self.base)
            self._run(0, s0, sched)
            st = e.msave()
            best_sc = None
            hist = {}
            done = False
            for j in range(cut1 - 2, s0, -1):
                if j in sched:
                    continue
                for b in SETS:
                    sc = dict(sched)
                    sc[j] = b
                    try:
                        c, k, lg = self._speech(sc, st, s0)
                    except RuntimeError:
                        continue
                    if c != cut1:
                        continue
                    hist[(k, lg)] = hist.get((k, lg), 0) + 1
                    if k + lg < skip + lag:
                        skip, lag, best_sc = k, lg, sc
                        self.log(f"  {fmt(b)} on offset {j}: press taken after {k} frames, tower back {lg} later ({k + lg})")
                        if k + lg <= M.SKIP_MIN + M.LAG_MIN:
                            done = True
                            break
                if done:
                    break
            e.mfree(st)
            self.log(f"  (skip, lag) seen over the tries: {sorted(hist.items())}")
            if best_sc is not None:
                sched = best_sc
        sched[cut1 + skip] = ("A",)
        back = cut1 + skip
        # replay the whole tail under the final schedule and idle to the T. Bird cut
        e.mload(self.base)
        self._run(0, back, sched)
        if e.byte(0x10) != 13:
            raise RuntimeError("the final schedule did not leave the speech on the expected frame")
        off = back
        prev = 13
        cut2 = None
        while off < back + 700:
            e.step((), 1)
            off += 1
            lv = e.byte(0x10)
            if prev == 13 and lv == 254:
                cut2 = off
                break
            prev = lv
        if cut2 is None:
            raise RuntimeError("no cut to T. Bird within 700 frames of the tower scene")
        self.frames_run += cut2 - back
        self.sched = sched
        tail = [fmt(sched.get(o, ())) for o in range(1, cut2 + 1)]
        res = {"flight": self.resp, "h0": self.h0, "n1": self.n1, "queen_speech_cut": cut1, "skip": skip, "lag": lag, "back": back,
               "tbird_cut": cut2, "tail_frames": cut2, "wait": cut2 - back - lag - 340, "tail": tail,
               "presses": sorted((o, fmt(b)) for o, b in sched.items())}
        self.log(f"TAIL: last hit +{cut1} = cut to the Queen's speech, +{back} = back on the tower (A on that frame), "
                 f"+{cut2} = cut to Professor T. Bird. Final wait {res['wait']} frames. Presses: {res['presses']}")
        return res

    def verify(self, tail: list[str]) -> int:
        """replay a tail from the last hit on a clean state; returns the T. Bird cut offset (None if it never comes)"""
        e = self.e
        e.mload(self.base)
        prev = 13
        cuts = []
        for i, b in enumerate(tail):
            e.step(bt(b), 1)
            lv = e.byte(0x10)
            if prev == 13 and lv == 254:
                cuts.append(i + 1)
            prev = lv
        return cuts[1] if len(cuts) > 1 else None


def append_tail(e: BizHawk, steer_s: float = 0, log=print) -> dict:
    """e has just executed the last-hit frame (the Queen's id reads 0x46). Plays the shortest legal ending found (steer_s
    seconds of dice search; 0 = the plain tail) and returns finish()'s dict: 'tail' = inputs after the last hit up to the
    T. Bird cut, 'tbird_cut' = frames from the last hit to that cut, 'queen_speech_cut', 'back', 'skip', 'lag', 'wait'."""
    en = Ending(e, log)
    en.measure()
    if steer_s:
        en.steer(steer_s)
    return en.finish(steer_skip=bool(steer_s))


def to_last_hit(e: BizHawk, ins: list[str], start: int = 0):
    """Play ins[start:] until the frame the Queen's id turns 0x46. Returns the number of inputs played (index of the hit
    frame, 1-based within ins) or None."""
    prev = None
    for i in range(start, len(ins)):
        e.step(bt(ins[i]), 1)
        ids = e.ram(M.T_ID, 15)
        cur = None
        for s in range(2, 15):
            if ids[s] in (M.QID, M.DEAD):
                cur = ids[s]
                break
        if prev == M.QID and cur == M.DEAD:
            return i + 1
        prev = cur if cur is not None else prev
    return None


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    opt = {}
    it = iter(argv)
    for a in it:
        if a.startswith("--"):
            opt[a[2:]] = next(it, None) if a[2:] in ("steer", "route", "state", "frame", "tol") else True
    args = [a for a in args if a not in opt.values()]
    seg, out = args[0], args[1]
    if (LOGS_DIR / f"pbeam_{out}.json").exists():
        sys.exit(f"logs/pbeam_{out}.json exists: use a fresh output name")
    FIX.mkdir(exist_ok=True)
    j = json.loads((LOGS_DIR / f"pbeam_{seg}.json").read_text())
    e = BizHawk(log_name=f"end_tail_{out}.log")
    logf = open(FIX / f"end_tail_{out}.txt", "w", encoding="utf-8")

    def log(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()

    if opt.get("route"):
        route = [l for l in open(LOGS_DIR / f"{opt['route']}.inputs.txt").read().splitlines() if not l.startswith("#")]
        f0 = int(opt["frame"])
        e.load(opt["state"])
        hit_abs = to_last_hit(e, route, f0)
        seg_start = None
        if hit_abs is None:
            sys.exit("no last hit found in the route")
        # the fight segment inside the route: its inputs must end where the route's do (it is the last segment)
        for cand in (len(route) - len(j["inputs"]),):
            if route[cand:cand + 50] == j["inputs"][:50]:
                seg_start = cand
        if seg_start is None:
            sys.exit("the segment is not the tail of that route")
        hit_idx = hit_abs - seg_start
        log(f"route {opt['route']}: last hit on frame {hit_abs} = input {hit_idx} of {seg}")
    else:
        e.load(j["bookmark"])
        hit_idx = to_last_hit(e, j["inputs"])
        hit_abs = None
        if hit_idx is None:
            sys.exit("no last hit: the Queen never turns into object 0x46 in this segment")
        log(f"{seg} from bookmark {j['bookmark']}: last hit on input {hit_idx}")
    en = Ending(e, log)
    pr = M.predict(en.m0, natural=True)
    log("prediction from the RAM at the last hit:", {k: v for k, v in pr.items()})
    en.measure()
    if opt.get("steer"):
        en.steer(float(opt["steer"]), tol=int(opt.get("tol") or 0))
    res = en.finish(steer_skip=bool(opt.get("steer")))
    chk = en.verify(res["tail"])
    log(f"clean replay of the tail from the last hit: T. Bird cut at +{chk} ({'SAME' if chk == res['tbird_cut'] else 'DIFFERENT'})")
    ins = j["inputs"][:hit_idx] + res["tail"] + [""] * 30
    end = {"last_hit": hit_idx, "queen_speech_cut": hit_idx + res["queen_speech_cut"], "back": hit_idx + res["back"],
           "tbird_cut": hit_idx + res["tbird_cut"], "tail_frames": res["tbird_cut"], "flight": res["flight"], "n1": res["n1"],
           "skip": res["skip"], "lag": res["lag"], "wait": res["wait"], "presses": res["presses"], "built_on": opt.get("state") or j["bookmark"],
           "predicted_best": pr["best"], "predicted_floor": pr["floor"]}
    if hit_abs is not None:
        end["route_frames"] = {"last_hit": hit_abs, "queen_speech_cut": hit_abs + res["queen_speech_cut"],
                               "back": hit_abs + res["back"], "tbird_cut": hit_abs + res["tbird_cut"]}
    note = j.get("note", "")
    json.dump({"bookmark": j["bookmark"], "inputs": ins, "note": note, "end": end}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
    log(f"wrote logs/pbeam_{out}.json: {len(ins)} inputs; last hit {end['last_hit']}, Queen's speech {end['queen_speech_cut']}, "
        f"T. Bird cut {end['tbird_cut']} (tail {end['tail_frames']} frames; up14's was 1168)" +
        (f"; in the route: T. Bird cut on frame {end['route_frames']['tbird_cut']}" if hit_abs is not None else ""))
    e.close()
    return end


if __name__ == "__main__":
    main(sys.argv[1:])
