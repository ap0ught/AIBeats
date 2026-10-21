"""u17p_port.py - NesHawk port of route up17 (track "NESHAWK PORT", 2026-10-10).

core_check_toads.py's `port` (lag-compensated feed by POLLED frame + Select re-rolls) with one addition, made here in a
subclass so that core_check_toads.py itself is not touched:

  RE-ALIGNMENT AT A TRANSITION. `port` assumes that both cores read the controller the same number of times between two
  points of the game. That held for up14 / up16b2. In up17 it does not at the end of Level 8: the level ends on a real-time
  event, and NesHawk gets one more polled frame in before the cut than quickerNES does. From there the old tool feeds every
  input one polled frame early and no Select re-roll can repair that (run u17p: stuck at reference frame 16176).
  Here, when the tracks part and do not meet again, and the level bytes differ or a load (a run of lag frames) lies just
  behind, the tool first tries to
      insert n idle polled frames on this core before reference polled index j   (this core polls more often), or
      skip   n reference polled frames from index j                              (this core polls less often),
  with j = the frame of the break or a lag-run boundary shortly before it, cheapest first, and keeps the first variant after
  which the reference's track holds for --align-hold polled frames. Only then the Select re-roll search runs.

  STRICT HITS (--strict-hits). `port` lets the tracks part for a while when they meet again by themselves. In up17's
  Robo-Manus fight that hid a lost blow: the toad's last attack is rolled by the dice, NesHawk rolled another one whose
  height track is the same for six frames, the boss died 2 game frames later, and the tracks "met again". The 2 frames are
  lost, and worse: every later input of Level 8 then arrives 2 game frames early, so the reference's cosmetic A,B mash
  reaches frames on which the toad still obeys (it jumps), and the de-mashed list no longer replays to the same RAM.
  With --strict-hits a passing difference in which a tracked enemy's (id, health) or the Queen's hit counter differs is
  first given to the Select re-roll search; only if that fails it is tolerated as before.

  PAGE OPTIMISATION (--page-opt). The card page between two levels takes more or fewer load frames depending on the hidden
  CPU alignment it is entered with (knowledge/u17f_notes.md); the reference's alignment was tuned for quickerNES. On the
  page's first polled frame the tool tries a Select toggle on each of the last --page-window polled frames of the level
  before it and keeps the one after which this core reaches polled frame (next level's first + --page-tail) soonest,
  provided the track, lives, health and score there are the reference's.

    python u17p_port.py port <tag> --ref <quickerNES capture tag> [--core NesHawk] [--end-steer S] [--mods-from <tag>]
                                   [--strict-hits] [--page-opt]

Output as core_check_toads.py port: logs/fix/core_<tag>.inputs.txt, core_<tag>.json (plus "insert_before_ref_frames",
"skip_ref_frames", "aligns"), two straight replays from power-on at the end (MATCH / MISMATCH).
Nothing here writes memory; savestates are used for the search only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import core_check_toads as cc
from core_check_toads import FIX, LEVEL, gkey, sha, parse_info, derived_bridge, emu_mod, banned


PLAY_LEVELS = (1, 3, 4, 8, 7, 11, 9, 10)     # level bytes behind which a card page follows (5 -> 13 has none)


class Porter2(cc.Porter):
    def __init__(self, a):
        super().__init__(a)
        self.inserts = {}          # reference polled index -> idle polled frames this core gets before it
        self.skips = set()         # reference polled indices that are not fed at all
        self.x = 0                 # inserted polls already done before index self.k
        self.aligns = []
        self.port_bounds = set()   # polled indices that followed a run of lag frames on this core
        self.page_log = []
        self.pages_done = set()
        self.hit_tried = set()
        self.hit_fixed = []
        self.ref_bounds = {j for j in range(1, self.K) if self.polled[j] - self.polled[j - 1] >= a.bound_gap}
        if a.mods_from:
            prev = json.loads((FIX / f"core_{a.mods_from}.json").read_text())
            idx = {f: i for i, f in enumerate(self.polled)}
            self.inserts = {idx[int(f)]: int(n) for f, n in prev.get("insert_before_ref_frames", {}).items()}
            self.skips = {idx[int(f)] for f in prev.get("skip_ref_frames", [])}
            print(f"[{a.tag}] starting with {sum(self.inserts.values())} inserted polls and {len(self.skips)} skipped "
                  f"reference polls from {a.mods_from}", flush=True)

    # ---------------------------------------------------------------- stepping
    def step(self):
        """one frame. None = nothing to compare (a lag frame, or an inserted idle poll), else whether the key matches
        the reference's polled frame"""
        while self.k in self.skips and self.k < self.K - 1:
            self.k += 1
            self.x = 0
        extra = self.x < self.inserts.get(self.k, 0)
        b = () if extra else self.inp(self.k)
        fc, lag, isl, hx = self.e.cmd("capstep " + (",".join(b) or "-")).split(" ")
        self.prev_ram = self.ram
        self.ram = bytes.fromhex(hx)
        del self.sent[self.t:]
        self.sent.append(b)
        self.t += 1
        if isl == "1":
            self.lagn += 1
            self.lag_run += 1
            if self.lag_run > 3000:
                raise RuntimeError(f"3000 lag frames in a row at frame {self.t}: the game is not reading the controller")
            return None
        if self.lag_run >= self.a.bound_gap - 1:
            self.port_bounds.add(self.k)
        self.lag_run = 0
        if extra:
            self.x += 1
            return None
        ok = gkey(self.ram, self.is_loose(self.k)) == self.rk(self.k)
        self.k += 1
        self.x = 0
        return ok

    def save(self):
        sid = self.e.cmd("msave")
        self.ring.append({"k": self.k, "t": self.t, "lagn": self.lagn, "sid": sid, "x": self.x})
        while len(self.ring) > self.a.ring:
            old = self.ring.pop(0)
            self.e.cmd(f"mfree {old['sid']}")

    def restore(self, ent, drop_later):
        super().restore(ent, drop_later)
        self.x = ent.get("x", 0)

    # ---------------------------------------------------------------- re-alignment
    def _apply(self, kind, j, n, sign):
        if kind == "insert":
            v = self.inserts.get(j, 0) + sign * n
            if v:
                self.inserts[j] = v
            else:
                self.inserts.pop(j, None)
        else:
            for i in range(j, j + n):
                if sign > 0:
                    self.skips.add(i)
                else:
                    self.skips.discard(i)

    def align_trial(self, kind, j, n, d):
        ent = self.entry_before(j - 1)
        if ent is None:
            return -1
        self.trials += 1
        if self.dirty is None or ent["k"] < self.dirty["k"]:
            self.dirty = ent
        self.restore(ent, drop_later=False)
        self._apply(kind, j, n, +1)
        goal = min(d + self.a.align_hold, self.K - 1)
        reach = goal + 1
        try:
            while self.k <= goal:
                ok = self.step()
                if ok is False and (self.k - 1) not in self.tolerated:
                    reach = self.k - 1
                    break
        finally:
            self._apply(kind, j, n, -1)
        return reach

    def realign(self, d, kd_ref, kd_cur):
        """the tracks part at polled index d for good. If that is a transition (level bytes differ, or a load lies just
        behind), try to shift the polled-frame mapping. True if a shift was accepted."""
        a = self.a
        lv_ref, lv_cur = kd_ref[5], kd_cur[5]
        lo = max(self.ring[0]["k"] + 1, d - a.align_window, 1) if self.ring else d
        bounds = sorted((j for j in (self.ref_bounds | self.port_bounds) if lo <= j <= d), reverse=True)
        if lv_ref == lv_cur and not bounds:
            return False
        t0 = time.time()
        n0 = self.trials
        cands = []
        js = [d] + [j for j in bounds if j != d]
        for j in js:
            for n in (1, 2, 3):
                cands.append(("insert", j, n))
                cands.append(("skip", j, n))
        need = min(d + a.align_hold, self.K - 1)
        best = None
        for kind, j, n in cands:
            r = self.align_trial(kind, j, n, d)
            if best is None or r > best[0]:
                best = (r, kind, j, n)
            if r > need:
                break
            if time.time() - t0 > a.align_seconds:
                break
        if best is None or best[0] < min(d + a.align_min, self.K - 1):
            print(f"[{a.tag}] no shift of the polled-frame mapping restores the track at reference frame {self.polled[d]} "
                  f"(best holds {best[0] - d if best else 0} polled frames, {self.trials - n0} tries)", flush=True)
            return False
        reach, kind, j, n = best
        self._apply(kind, j, n, +1)
        self.aligns.append({"polled_index": d, "ref_frame": self.polled[d], "kind": kind, "at_polled_index": j,
                            "at_ref_frame": self.polled[j], "n": n, "holds_polled_frames": reach - d,
                            "level_ref": int(lv_ref), "level_here": int(lv_cur), "tries": self.trials - n0,
                            "seconds": round(time.time() - t0, 1)})
        what = (f"{n} idle polled frame(s) inserted on this core before reference frame {self.polled[j]}" if kind == "insert"
                else f"{n} reference polled frame(s) from {self.polled[j]} not fed")
        print(f"[{a.tag}] re-alignment #{len(self.aligns)} at reference frame {self.polled[d]} (level byte reference {lv_ref}, "
              f"here {lv_cur}): {what}; the track then holds {reach - d}+ polled frames, {self.trials - n0} tries, "
              f"{time.time() - t0:.0f}s", flush=True)
        self.clean()
        return True

    def resync(self):
        """after a savestate load: this state's RAM (so that the next frame is compared with the right 'previous' one)
        and the level log without the rows of the abandoned timeline. Returns the level byte."""
        fc, lag, isl, hx = self.e.cmd("capnow").split(" ")
        self.ram = bytes.fromhex(hx)
        self.level_log = [c for c in self.level_log if c["frame"] <= self.t]
        return self.ram[LEVEL]

    # ---------------------------------------------------------------- strict hits
    @staticmethod
    def hitkey(m):
        """what a blow changes: level, the Queen's hit counter, the tracked enemies' (id, health)"""
        if not isinstance(m, (bytes, bytearray)):
            m = bytes(m)
        return (m[LEVEL], m[0x586] if m[LEVEL] == 13 else 0,
                tuple(sorted((m[0x3C1 + q], m[0x51A + q]) for q in range(2, 15) if m[0x3C1 + q] in cc.TRACK_IDS)))

    # ---------------------------------------------------------------- page optimisation
    def _page_run(self, kt):
        """play on until reference polled index kt has been fed; this core's frame number then, or None if the track
        left the reference's or lives / health / score differ there"""
        while self.k <= kt:
            ok = self.step()
            if ok is False and (self.k - 1) not in self.tolerated:
                return None
        m, r = self.ram, bytes(self.refram[self.polled[kt]])
        if m[0x11] != r[0x11] or m[0x51A] != r[0x51A] or m[0x5F4:0x5FA] != r[0x5F4:0x5FA]:
            return None
        return self.t

    def page_opt(self, kp):
        """kp = the page's first polled index, just fed and matched. Tries one Select toggle on each of the last
        page_window polled frames before it."""
        a = self.a
        lvl = lambda k: int(self.refram[self.polled[k]][LEVEL])
        kn = kp
        while kn < self.K - 1 and lvl(kn) in (254, 255):
            kn += 1
        kt = min(kn + a.page_tail, self.K - 1)
        self.save()
        here = self.ring[-1]
        t0 = time.time()
        t_base = self._page_run(kt)
        if t_base is None:
            self.restore(here, drop_later=True)
            print(f"[{a.tag}] page at reference frame {self.polled[kp]}: the plain run does not hold to reference frame "
                  f"{self.polled[kt]}; left as it is", flush=True)
            return False
        best = (t_base, None)
        lo = max(self.ring[0]["k"] + 1, kp - a.page_window)
        n = ok_n = 0
        seen = {}
        # nearest first; every frame for the first page_dense polled frames, then every page_step-th (a forced end-of-level
        # walk ignores the pad altogether: a toggle there changes nothing, the useful frames lie before it)
        cand = [j for j in range(kp - 1, lo - 1, -1) if kp - j <= a.page_dense or (kp - j) % a.page_step == 0]
        for j in cand:
            ent = self.entry_before(j)
            if ent is None:
                break
            if self.dirty is None or ent["k"] < self.dirty["k"]:
                self.dirty = ent
            self.restore(ent, drop_later=False)
            self.mods ^= {j}
            try:
                t = self._page_run(kt)
            finally:
                self.mods ^= {j}
            n += 1
            self.trials += 1
            if t is not None:
                ok_n += 1
                seen[t - t_base] = seen.get(t - t_base, 0) + 1
                if t < best[0]:
                    best = (t, j)
            if time.time() - t0 > a.page_seconds:
                break
        rec = {"page_first_polled_ref_frame": self.polled[kp], "next_level": lvl(kn), "measured_at_ref_frame": self.polled[kt],
               "plain_frame": t_base, "tries": n, "valid": ok_n, "frames_against_plain": {str(k): v for k, v in sorted(seen.items())},
               "seconds": round(time.time() - t0, 1)}
        if best[1] is None:
            # BUG FIXED 2026-10-10 (run u17p2: its list did not replay, verify said MISMATCH): going straight back to
            # `here` left the last trial's Select in self.sent between the trial's start and `here`. Like repair(): go
            # back to the earliest state any trial touched and play it again without the toggle.
            if self.dirty is not None:
                self.clean()
            else:
                self.restore(here, drop_later=True)
            rec["chosen"] = None
            self.page_log.append(rec)
            print(f"[{a.tag}] page at reference frame {self.polled[kp]} (to level byte {lvl(kn)}): no Select toggle in the last "
                  f"{kp - lo} polled frames makes it shorter ({n} tries, {ok_n} valid, frames against plain {rec['frames_against_plain']}, "
                  f"{time.time() - t0:.0f}s)", flush=True)
            return False
        self.mods ^= {best[1]}
        rec["chosen"] = {"select_on_ref_frame": self.polled[best[1]], "polled_frames_before_page": kp - best[1],
                         "frame": best[0], "gain": t_base - best[0]}
        self.page_log.append(rec)
        print(f"[{a.tag}] page at reference frame {self.polled[kp]} (to level byte {lvl(kn)}): Select toggled {kp - best[1]} polled "
              f"frames before it (reference frame {self.polled[best[1]]}): reference frame {self.polled[kt]} is reached on frame "
              f"{best[0]} instead of {t_base} ({t_base - best[0]} frames sooner; {n} tries, {ok_n} valid, frames against plain "
              f"{rec['frames_against_plain']}, {time.time() - t0:.0f}s)", flush=True)
        self.clean()
        return True

    # ---------------------------------------------------------------- output
    def write(self, done):
        super().write(done)
        p = FIX / f"core_{self.a.tag}.json"
        summ = json.loads(p.read_text())
        summ["insert_before_ref_frames"] = {str(self.polled[j]): n for j, n in sorted(self.inserts.items())}
        summ["skip_ref_frames"] = sorted(self.polled[j] for j in self.skips)
        summ["aligns"] = self.aligns
        summ["page_opt"] = self.page_log
        summ["strict_hit_rerolls"] = self.hit_fixed
        summ["tool"] = "u17p_port.py"
        tmp = FIX / f"core_{self.a.tag}.json.tmp"
        tmp.write_text(json.dumps(summ, indent=1))
        tmp.replace(p)

    # ---------------------------------------------------------------- main loop (core_check_toads.Porter.go + realign)
    def go(self):
        a = self.a
        os.environ["TOADS_CORE"] = a.core
        emu_mod.BRIDGE_LUA = derived_bridge()
        self.e = e = emu_mod.BizHawk(log_name=f"fix_core_{a.tag}.log", fields={})
        self.info = parse_info(e.cmd("coreinfo"))
        print(f"[{a.tag}] loaded: {self.info['core_seen']} (board {self.info['board']}); {self.K} polled inputs to place", flush=True)
        if self.info["core_seen"].lower() != a.core.lower():
            e.close()
            raise SystemExit("wrong core loaded")
        self.t0 = time.time()
        self.dirty = None
        self.ending = None
        self.prev_ram = None
        self.want_more = False
        self.loose_level = None
        prev_lv = None
        last_report = 0
        stuck = None
        ended = False
        try:
            while self.k < self.K and self.t < a.max_frames:
                ok = self.step()
                lv = self.ram[LEVEL]
                if lv != prev_lv:
                    if prev_lv is not None:
                        rf = self.polled[min(self.k, self.K - 1)]
                        fresh = not any(c["frame"] == self.t and c["to"] == lv for c in self.level_log)
                        self.level_log = [c for c in self.level_log if c["frame"] < self.t]
                        self.level_log.append({"frame": self.t, "from": prev_lv, "to": lv, "next_ref_polled_frame": rf, "lag": self.lagn})
                        if fresh:
                            print(f"[{a.tag}] frame {self.t}: level byte {prev_lv} -> {lv}  (next reference polled frame {rf}, "
                                  f"offset {self.t - rf:+d})  re-rolls so far {len(self.repairs)}", flush=True)
                    if self.loose and prev_lv is not None and lv not in (254, 255) and lv != self.loose_level:
                        self.loose_spans.append((self.loose_from[-1], self.k - 1))
                        self.loose = False
                    prev_lv = lv
                if ok is None:
                    continue
                if ok:
                    if a.end_steer and self.last_hit_now():
                        self.steered_ending()
                        ended = True
                        break
                    kp = self.k - 1
                    # the first polled frame of a card page (it can read 254 or 255: Level 3 -> 4's reads 255), or of
                    # Level 13 behind the tower (no cards there, but a load)
                    rl, rl0 = (int(self.refram[self.polled[kp]][LEVEL]), int(self.refram[self.polled[kp - 1]][LEVEL])) if kp > 0 else (0, 0)
                    if (a.page_opt and kp not in self.pages_done and kp > 0 and lv == rl
                            and ((rl in (254, 255) and rl0 in PLAY_LEVELS) or (rl == 13 and rl0 == 5))):
                        self.pages_done.add(kp)
                        self.page_opt(kp)
                        prev_lv = self.resync()
                        continue
                    if self.k % a.every == 0:
                        self.save()
                    if self.k - last_report >= 3000:
                        last_report = self.k
                        print(f"[{a.tag}] frame {self.t} = reference frame {self.polled[self.k - 1]}, level {lv}, "
                              f"{len(self.repairs)} re-rolls, {self.trials} tries, {time.time() - self.t0:.0f}s", flush=True)
                    continue
                d = self.k - 1
                if d in self.tolerated:
                    continue
                base = self.entry_before(d)
                kd_ref, kd_cur = self.rk(d), gkey(self.ram, self.is_loose(d))
                if a.verbose:
                    print(f"[{a.tag}] frame {self.t}, reference frame {self.polled[d]}: key differs: reference {kd_ref}  here {kd_cur}", flush=True)
                run_ok, bad = 0, [d]
                hk_bad = self.hitkey(self.ram) != self.hitkey(self.refram[self.polled[d]])
                while self.k < min(self.K, d + a.look) and run_ok < a.rejoin:
                    o = self.step()
                    if o is None:
                        continue
                    if o:
                        run_ok += 1
                    else:
                        run_ok = 0
                        bad.append(self.k - 1)
                        hk_bad = hk_bad or self.hitkey(self.ram) != self.hitkey(self.refram[self.polled[self.k - 1]])
                if (run_ok >= a.rejoin or self.k >= self.K) and a.strict_hits and hk_bad and base is not None and d not in self.hit_tried:
                    self.hit_tried.add(d)
                    print(f"[{a.tag}] reference frame {self.polled[d]}: the tracks part for {bad[-1] - d + 1} polled frames and meet "
                          f"again, but a blow lands on another frame (reference {kd_ref}  here {kd_cur}); searching a re-roll that "
                          f"puts it back", flush=True)
                    keep = (a.random_tries, a.strict_random)
                    a.random_tries = a.strict_random = a.hit_random
                    try:
                        fixed = self.repair(d)
                    finally:
                        a.random_tries, a.strict_random = keep
                    if fixed:
                        self.hit_fixed.append(self.polled[d])
                        prev_lv = self.resync()
                        continue
                    print(f"[{a.tag}] reference frame {self.polled[d]}: no re-roll puts the blow back; tolerated", flush=True)
                    self.tolerated.update(bad)
                    prev_lv = self.resync()
                    continue
                if run_ok >= a.rejoin or self.k >= self.K:
                    self.tolerated.update(bad)
                    print(f"[{a.tag}] reference frame {self.polled[d]}: the tracks part for {bad[-1] - d + 1} polled frames "
                          f"({len(bad)} differ) and meet again by themselves", flush=True)
                    prev_lv = self.ram[LEVEL]
                    continue
                print(f"[{a.tag}] frame {self.t}: the tracks part at reference frame {self.polled[d]} (level {int(self.refram[self.polled[d]][LEVEL])}) "
                      f"and do not meet again: reference {kd_ref}  here {kd_cur}; searching", flush=True)
                fixed = base is not None and self.realign(d, kd_ref, kd_cur)
                if not fixed:
                    fixed = base is not None and self.repair(d)
                if not fixed and base is not None and not self.is_loose(d):
                    self.loose = True
                    self.loose_level = int(self.refram[self.polled[d]][LEVEL])
                    self.loose_from.append(base["k"])
                    print(f"[{a.tag}] no re-roll restores the enemy's exact position at reference frame {self.polled[d]}: "
                          f"switching to the loose key (toad, enemy health, hit counter) until the level ends", flush=True)
                    if self.k > base["k"]:
                        self.restore(base, drop_later=True)
                    prev_lv = self.resync()
                    continue
                if not fixed:
                    stuck = d
                    print(f"[{a.tag}] STUCK at reference frame {self.polled[d]} (polled index {d}): no shift and no Select pattern in "
                          f"the last {a.window} polled frames restores the reference's track ({self.trials} tries in all)", flush=True)
                    if base is not None and self.k > base["k"]:
                        self.restore(base, drop_later=True)
                    break
                prev_lv = self.resync()
            cuts = lambda: sum(1 for c in self.level_log if c["from"] == 13 and c["to"] == 254)
            if stuck is None and not ended and self.k >= self.K and cuts() < 2:
                prev = self.ram[LEVEL]
                for _ in range(2500):
                    fc, lag, isl, hx = e.cmd("capstep -").split(" ")
                    self.ram = bytes.fromhex(hx)
                    self.sent.append(())
                    self.t += 1
                    lv = self.ram[LEVEL]
                    if lv != prev:
                        self.level_log.append({"frame": self.t, "from": prev, "to": lv, "next_ref_polled_frame": None, "lag": None})
                        if prev == 13 and lv == 254 and cuts() >= 2:
                            print(f"[{a.tag}] frame {self.t}: cut to T. Bird (after the reference's inputs ran out)", flush=True)
                            break
                        prev = lv
        finally:
            done = stuck is None and (ended or self.k >= self.K)
            self.write(done)
            e.close()
        print(f"[{a.tag}] {'COMPLETE' if done else 'INCOMPLETE'}: {self.k}/{self.K} polled inputs in {self.t} frames "
              f"({self.lagn} lag), {len(self.repairs)} re-rolls, {len(self.aligns)} re-alignments ({self.trials} tries), "
              f"{time.time() - self.t0:.0f}s", flush=True)
        if done and a.verify:
            self.verify()


def port(a):
    FIX.mkdir(parents=True, exist_ok=True)
    if a.loose_level is None:
        a.loose_level = [13]
    Porter2(a).go()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    po = sub.add_parser("port")
    po.add_argument("tag")
    po.add_argument("--ref", default="u17q")
    po.add_argument("--core", default="NesHawk")
    po.add_argument("--first-poll", type=int, default=100)
    po.add_argument("--every", type=int, default=6)
    po.add_argument("--ring", type=int, default=70)
    po.add_argument("--window", type=int, default=180)
    po.add_argument("--hold", type=int, default=12)
    po.add_argument("--look", type=int, default=900)
    po.add_argument("--rejoin", type=int, default=60)
    po.add_argument("--random-tries", type=int, default=1200)
    po.add_argument("--strict-random", type=int, default=300)
    po.add_argument("--max-frames", type=int, default=70000)
    po.add_argument("--verbose", action="store_true")
    po.add_argument("--mods-from", default=None)
    po.add_argument("--best-of", type=int, default=2)
    po.add_argument("--extra", type=int, default=90)
    po.add_argument("--loose-level", type=int, action="append", default=None)
    po.add_argument("--verify", type=int, default=2)
    po.add_argument("--end-steer", type=float, default=0)
    po.add_argument("--align-hold", type=int, default=300)     # polled frames the track must hold after a shift
    po.add_argument("--align-min", type=int, default=40)       # ... or at least this many, if none holds that long
    po.add_argument("--align-window", type=int, default=240)   # how far back a lag-run boundary may lie
    po.add_argument("--align-seconds", type=float, default=240)
    po.add_argument("--bound-gap", type=int, default=30)       # reference frames between two polled frames that count as a load
                                                              # (5 also catches the hit-stops of a fight: hundreds of useless tries)
    po.add_argument("--strict-hits", action="store_true")      # re-roll a passing difference in which a blow lands on another frame
    po.add_argument("--hit-random", type=int, default=150)     # ... with at most this many multi-press tries
    po.add_argument("--page-opt", action="store_true")         # shorten each card page on this core with one Select toggle before it
    po.add_argument("--page-window", type=int, default=90)     # ... on one of this many polled frames before the page
    po.add_argument("--page-tail", type=int, default=60)       # ... measured this many polled frames into the next level
    po.add_argument("--page-dense", type=int, default=90)      # ... every frame this close to the page,
    po.add_argument("--page-step", type=int, default=1)        # ... every N-th frame farther back
    po.add_argument("--page-seconds", type=float, default=300)
    a = ap.parse_args()
    if not a.tag.startswith("u17"):
        sys.exit("this track owns logs/fix/core_u17* only: use a tag that starts with u17")
    port(a)
