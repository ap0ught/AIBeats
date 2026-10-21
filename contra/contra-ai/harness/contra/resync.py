"""Tools for fitting someone else's input log (a TAS made on another emulator / ROM revision) to this harness.

The game's random number ($34) is advanced by the idle loop, so it depends on exact CPU timing and differs between
emulators; a foreign input log therefore drifts wherever luck matters and has to be re-fitted piece by piece.

Pool(n)                     n emulators, each on its own thread
play(emu, state, rows)      load a savestate, play rows, stop early on death / level change, return a Result
"""
from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field

from .emulator import BizHawk

F = {"level": 0x30, "lives": 0x32, "groutine": 0x18, "lroutine": 0x2C, "pstate": 0x90, "death": 0xB4,
     "screen": 0x64, "scroll": 0x65, "gameover": 0x38, "bossdef": 0x3B, "endidx": 0x19, "x": 0x334, "y": 0x31A,
     "weapon": 0xAA, "fc": 0x1A, "rng": 0x34, "cleared": 0x37, "loc": 0x40, "hud": 0x6A, "elr": 0x2D, "elec": 0xC8, "adv": 0xD0}


@dataclass
class Result:
    reason: str                 # "death" | "elec" (walked into a base fence) | "level" | "eof" | "gameover" | "end"
    frames: int                 # frames played before the stop (index into rows of the frame that showed it)
    frame: int                  # emulator frame counter at the stop
    last: dict = field(default_factory=dict)
    progress: int = 0           # screen*256+scroll high-water mark
    trace: list = field(default_factory=list)
    lag: int = 0
    tag: object = None

    def key(self):
        """Bigger is better: finishing the level beats everything, then how long / how far it got."""
        if self.reason in ("level", "end"):
            return (2, -self.frames, 0)
        return (1 if self.reason == "eof" else 0, self.progress, self.frames)

    def __str__(self):
        l = self.last
        return (f"{self.reason:8s} after {self.frames:5d} f (emu frame {self.frame}) level {l.get('level')} "
                f"screen {l.get('screen')}.{l.get('scroll')} x {l.get('x')} y {l.get('y')} bossdef {l.get('bossdef')} "
                f"progress {self.progress}")


def play(emu: BizHawk, state: str | None, rows, chunk: int = 120, keep_trace: bool = False,
         stop_on_death: bool = True, stop_on_level: bool = True, stall: int = 0, comp: bool = True) -> Result:
    """Load `state` (None = continue from where the emulator is) and play rows. Stops at the first death
    ($B4 bit 0 rising), at a change of the level byte, at game over, or at the end of rows."""
    if state is not None:
        emu.load(state)
    emu.set_fields(F) if emu.fields != F else None
    emu.trace(True)
    s0 = emu.state()
    lvl0 = s0["level"]
    prev_death = s0["death"] & 1
    prev_elec = s0.get("elec", 0)
    prev_adv, prev_cleared = s0.get("adv", 0), s0.get("cleared", 0)
    prog = 0
    last_gain = 0
    n = 0
    trace = []
    last = s0
    lag0 = s0["lag"]
    reason = "eof"
    rows = list(rows)
    sent_rows = []
    carry = 0
    for i in range(0, len(rows), chunk):
        if comp:
            _, sent, carry = emu.run_comp(rows[i:i + chunk], chunk=chunk, carry=carry)
            sent_rows.extend(sent)
        else:
            emu.run(rows[i:i + chunk], chunk=chunk)
            sent_rows.extend(rows[i:i + chunk])
        tr = emu.last_trace
        stop = False
        for j, s in enumerate(tr):
            if keep_trace:
                trace.append(s)
            last = s
            n = i + j + 1
            if s["level"] == lvl0 and s["lroutine"] in (4, 8, 9):
                pg = s["screen"] * 256 + s["scroll"] + (100000 if s["bossdef"] else 0)
                if pg > prog:
                    prog, last_gain = pg, i + j + 1
            if stall and stop_on_death and (i + j + 1) - last_gain > stall:
                reason, stop = "stall", True
                break
            d = s["death"] & 1
            if stop_on_death and d and not prev_death:
                reason, stop = "death", True
                break
            prev_death = d
            # base rooms: Up before the fence is down = 48 frames of stun. The movie never does that on purpose,
            # so it means the room was cleared later than the movie expects.
            el = s.get("elec", 0)
            if stop_on_death and el and not prev_elec:
                reason, stop = "elec", True
                break
            prev_elec = el
            # the walk to the next room must start the frame AFTER $37 reads $80. An Up read on the frame the
            # flag is set still starts the walk, but one frame late, and the movie's next three Ups are then
            # each read one frame too early and ignored.
            ad = s.get("adv", 0)
            if stop_on_death and ad and not prev_adv and prev_cleared != 0x80 and s["loc"] == 1 and s["level"] == lvl0:
                reason, stop = "elec", True
                break
            prev_adv, prev_cleared = ad, s["cleared"]
            if s["gameover"]:
                reason, stop = "gameover", True
                break
            if s["groutine"] == 6:
                reason, stop = "end", True
                break
            if stop_on_level and s["level"] != lvl0:
                reason, stop = "level", True
                break
        if stop:
            break
    emu.trace(False)
    res = Result(reason, n, last["frame"], dict(last), prog, trace, last["lag"] - lag0)
    res.last_gain = last_gain
    res.sent = sent_rows[:n]              # what was really sent for the frames up to the stop (lost presses repeated)
    return res


class Pool:
    """n emulators on n threads. map(jobs) runs fn(emu, job) for every job and returns results in order."""

    def __init__(self, n: int = 4, core: str | None = None, name: str = "pool"):
        self.emus = []
        errs = []

        def boot(i):
            try:
                self.emus.append(BizHawk(log_name=f"{name}_{i}.log", fields=F, core=core))
            except Exception as ex:           # noqa: BLE001
                errs.append(ex)
        th = [threading.Thread(target=boot, args=(i,)) for i in range(n)]
        for t in th:
            t.start()
        for t in th:
            t.join()
        if errs:
            self.close()
            raise errs[0]

    def map(self, fn, jobs):
        jobs = list(jobs)
        q = queue.Queue()
        for i, j in enumerate(jobs):
            q.put((i, j))
        out = [None] * len(jobs)
        errs = []

        def work(emu):
            while True:
                try:
                    i, j = q.get_nowait()
                except queue.Empty:
                    return
                try:
                    out[i] = fn(emu, j)
                except Exception as ex:       # noqa: BLE001
                    errs.append(ex)
                    return
        th = [threading.Thread(target=work, args=(e,)) for e in self.emus]
        for t in th:
            t.start()
        for t in th:
            t.join()
        if errs:
            raise errs[0]
        return out

    def close(self):
        for e in self.emus:
            try:
                e.close()
            except Exception:                 # noqa: BLE001
                pass
        self.emus = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ---------------------------------------------------------------- luck re-rolling ("repair")
import json
import random
import time

from .emulator import LOGS_DIR

def apply_edit(rows, ed):
    kind, t = ed[0], ed[1]
    rows = list(rows)
    if kind == "B+":
        rows[t] = tuple(rows[t]) + ("B",) if "B" not in rows[t] else rows[t]
    elif kind == "B-":
        rows[t] = tuple(b for b in rows[t] if b != "B")
    elif kind == "A+":
        for k in range(t, min(t + 4, len(rows))):
            if "A" not in rows[k]:
                rows[k] = tuple(rows[k]) + ("A",)
    elif kind == "dup":
        rows.insert(t, rows[t])
    elif kind == "del":
        del rows[t]
    elif kind == "P":                        # pause for k frames: Start, k-1 frames paused, Start again.
        # Game logic is frozen while paused (the frame counter and the idle-loop random number keep running),
        # so this changes the luck and nothing else. Costs k frames of real time.
        k = ed[2]
        rows[t:t] = [("Start",)] + [()] * (k - 1)
        rows[t + k] = tuple(rows[t + k]) + (("Start",) if "Start" not in rows[t + k] else ())
    elif kind == "wait":                     # n frames of nothing before row t (wait for a base fence to drop)
        rows[t:t] = [()] * ed[2]
    elif kind == "loop":                     # repeat the L rows before t, n times, before going on (more of the
        L, n = ed[2], ed[3]                  # movie's own attack pattern; everything after is delayed by L*n)
        pat = rows[max(0, t - L):t]
        rows[t:t] = pat * n
    elif kind == "cyc":                      # n rows taken cyclically from the L rows before t (all buttons)
        L, n = ed[2], ed[3]
        pat = rows[max(0, t - L):t] or [()]
        rows[t:t] = [pat[i % len(pat)] for i in range(n)]
    elif kind == "hold":                     # n rows of one button at t (t = len(rows) appends)
        rows[t:t] = [(ed[2],) if ed[2] else ()] * ed[3]
    elif kind == "loopwait":                 # n frames taken cyclically from the L rows before t, without Up
        L, n = ed[2], ed[3]
        pat = [tuple(b for b in r if b != "Up") for r in rows[max(0, t - L):t]] or [()]
        rows[t:t] = [pat[i % len(pat)] for i in range(n)]
    elif kind == "U+":                       # aim up for 3 frames (changes what the bullets hit, and the luck)
        for k in range(t, min(t + 3, len(rows))):
            if "Up" not in rows[k] and "Down" not in rows[k]:
                rows[k] = tuple(rows[k]) + ("Up",)
    return rows


def rand_edit(rng, rows, lo, hi, kinds):
    for _ in range(50):
        kind = rng.choice(kinds)
        t = rng.randrange(lo, max(lo + 1, hi))
        if kind == "B+" and "B" in rows[t]:
            continue
        if kind == "B-" and "B" not in rows[t]:
            continue
        if kind == "A+" and any("A" in rows[k] for k in range(max(0, t - 2), min(len(rows), t + 6))):
            continue
        if kind == "P":
            if any("Start" in rows[k] for k in range(max(0, t - 3), min(len(rows), t + 3))):
                continue
            return (kind, t, rng.choice((2, 2, 3, 3, 4, 5, 6, 7, 8, 9)))
        return (kind, t)
    return ("dup", lo)




def edit_cost(ed) -> int:
    """Frames of real time an edit adds."""
    if ed[0] == "loop":
        return ed[2] * ed[3]
    if ed[0] in ("loopwait", "cyc", "hold"):
        return ed[3]
    return {"P": ed[2] if len(ed) > 2 else 0, "wait": ed[2] if len(ed) > 2 else 0, "dup": 1, "del": -1}.get(ed[0], 0)


def repair_stage(pool: "Pool", state: str, rows, out: str, W: int = 240, H: int = 900, K: int = 12, seed: int = 1,
                 maxiter: int = 120, edits=None, meta=None, log=print, kinds0=("B+", "B+", "B+", "P", "P", "P"),
                 stall: int = 1800):
    """Play `rows` from savestate `state`; wherever it fails, repair and go on. Returns (done, rows, edits).

    Failures and repairs:
      death  - K random small edits in the W frames before it (see apply_edit); keep the one that gets furthest
               (progress first, then frames survived minus the frames the edit costs)
      elec   - the movie pressed Up at a base fence that is not down yet (the room was cleared later than in the
               movie's own game): insert exactly as many empty frames before that Up as it takes for the fence to drop
      stall  - no progress for `stall` frames: same random search around the place progress stopped
    rows are cut at the frame on which the level byte changes. Progress is saved to logs/<out>.seg.json."""
    rows = [tuple(r) for r in rows]
    edits = [tuple(e) for e in (edits or [])]
    for ed in edits:
        rows = apply_edit(rows, ed)
    rng = random.Random(seed + 1000 * len(edits))
    ck = {0: state}
    t00 = time.time()
    segp = LOGS_DIR / f"{out}.seg.json"
    segp.parent.mkdir(parents=True, exist_ok=True)
    e0 = pool.emus[0]

    def save(done, total):
        tmp = segp.with_name(segp.name + ".tmp")
        j = dict(meta or {})
        j.update({"state": state, "edits": edits, "done": done, "frames": total,
                  "rows": ["+".join(r) for r in (rows[:total] if done else [])]})
        tmp.write_text(json.dumps(j, indent=0), encoding="utf-8")
        tmp.replace(segp)

    def checkpoint(idx):
        if idx in ck:
            return ck[idx]
        base = max(k for k in ck if k <= idx)
        play(e0, ck[base], rows[base:idx], stop_on_death=False, stop_on_level=False)
        name = f"tmp/{out}_ck{idx}"
        e0.save(name)
        ck[idx] = name
        return name

    def drop_ck(after):
        for k in [k for k in ck if k > after]:
            del ck[k]

    fails = 0
    for it in range(maxiter):
        base = max(ck)
        r = play(e0, ck[base], rows[base:], stall=stall)
        D = base + r.frames
        log(f"[{out}] iter {it}: from {base}: {r}  (t+{time.time() - t00:.0f}s)")
        if r.reason in ("level", "end"):
            # one pass from the stage state: keep what was really sent (lost presses repeated a frame later),
            # which replays open-loop. If that pass does not finish (a carry at a checkpoint edge), go on repairing.
            full = play(e0, state, rows, stall=stall)
            if full.reason not in ("level", "end"):
                log(f"[{out}]    full pass from the stage state differs from the checkpointed one: {full}")
                ck.clear()
                ck[0] = state
                continue
            D = full.frames
            n_comp = sum(1 for a, b in zip(full.sent, rows) if tuple(a) != tuple(b))
            rows = [tuple(x) for x in full.sent]
            check = play(e0, state, rows, stall=stall, comp=False)
            if check.reason not in ("level", "end") or check.frames != D:
                log(f"[{out}]    open-loop check of the kept rows FAILED: {check}")
                return False, rows, edits
            meta = dict(meta or {})
            meta["lost_presses_repeated"] = n_comp
            save(True, D)
            log(f"[{out}] DONE: {D} frames from the stage state, {len(edits)} edits, {n_comp} rows changed by "
                f"lost-press compensation: {edits}")
            return True, rows, edits
        if r.reason == "eof" and len(rows) < 7000 and not any(e[0] == "hold" for e in edits):
            t = len(rows)
            c0 = max(k for k in ck if k <= max(0, t - 200))
            pat = rows[max(0, t - 48):t] or [()]
            x = play(e0, ck[c0], rows[c0:] + [pat[i % len(pat)] for i in range(2000)], keep_trace=True,
                     stop_on_level=False)
            b = next((i for i, st_ in enumerate(x.trace) if i >= t - c0 and st_["bossdef"] == 1), None)
            if x.reason in ("eof", "end", "level") and b is not None:
                n = (c0 + b + 1) - t
                for ed in (("cyc", t, 48, n), ("hold", t + n, "Up", 700), ("hold", t + n + 700, "", 700)):
                    rows = apply_edit(rows, ed)
                    edits.append(ed)
                log(f"[{out}]    the movie's rows ended at {t} with the boss alive: repeated its last 48 rows for {n} "
                    f"frames (boss defeated flag set), then Up held")
                save(False, 0)
                continue
            log(f"[{out}]    the movie's rows ended at {t}; repeating its last rows did not finish the boss: {x}")
        if r.reason in ("eof", "gameover"):
            log(f"[{out}] {r.reason} without finishing the stage: {r}")
            save(False, 0)
            return False, rows, edits
        if r.reason == "elec":
            up = D - 1                                   # the row whose Up was read on the frame the stun began
            c0 = max(0, up - 30)
            drop_ck(c0)
            cname = checkpoint(c0)
            LW = 26
            pat = [tuple(b for b in r if b != "Up") for r in rows[max(0, up - LW):up]] or [()]
            x = play(e0, cname, rows[c0:up] + [pat[i % len(pat)] for i in range(600)], keep_trace=True,
                     stop_on_death=False, stop_on_level=False)
            j = next((i for i, s in enumerate(x.trace) if i >= up - c0 - 1 and s["cleared"] == 0x80), None)
            if j is not None:
                n = max(1, (c0 + j) - up + 1)            # Up must be read on the frame AFTER the flag reads $80
                ed = ("loopwait", up, LW, n)
                rows = apply_edit(rows, ed)
                edits.append(ed)
                log(f"[{out}]    fence still up at row {up}: waiting {n} frames")
                save(False, 0)
                fails = 0
                continue
            log(f"[{out}]    fence at row {up}: the room is not cleared within 600 frames -> random search")
        if r.reason == "stall":
            D = min(D, r.last_gain + 450)
        b_prog = r.progress
        w = W * (2 ** min(fails, 3)) * (2 if r.reason != "death" else 1)
        kinds = list(kinds0) + (["dup", "del", "A+", "U+", "B-"] if fails >= 2 else [])
        w0 = max(0, D - w)
        drop_ck(w0)
        cname = checkpoint(w0)
        cands = [rand_edit(rng, rows, w0, max(w0 + 1, D - 6), kinds) for _ in range(K * (1 + min(fails, 2)))]
        lg = base + getattr(r, "last_gain", 0)
        boss_cands = []
        if D - lg > 120 and fails < 2:
            # where does the movie stop shooting after progress stopped? (last B before 30 rows without one)
            t = None
            lastb = None
            for i in range(lg, min(D, len(rows) - 31)):
                if "B" in rows[i]:
                    lastb = i
                elif lastb is not None and i - lastb >= 30:
                    t = lastb + 1
                    break
            if t is not None:
                c0 = max(0, t - 100)
                drop_ck(c0)
                cn = checkpoint(c0)
                HPF = dict(F)
                for sl in range(16):
                    HPF[f"hp{sl}"] = 0x578 + sl
                    HPF[f"ty{sl}"] = 0x528 + sl
                    HPF[f"rt{sl}"] = 0x4B8 + sl
                pat = rows[max(0, t - 48):t] or [()]
                e0.load(cn)
                e0.set_fields(HPF)
                e0.trace(True)
                e0.run_comp(rows[c0:t] + [pat[i % len(pat)] for i in range(1500)])
                tr = e0.last_trace
                e0.trace(False)
                e0.set_fields(F)
                at = tr[t - c0 - 1]
                slots = [sl for sl in range(16) if at[f"rt{sl}"] and at[f"ty{sl}"] != 1 and at[f"hp{sl}"] > 8]
                if slots:
                    bs = max(slots, key=lambda sl: at[f"hp{sl}"])
                    e_hp = next((i for i in range(t - c0, len(tr)) if tr[i][f"hp{bs}"] == 0 or tr[i][f"ty{bs}"] != at[f"ty{bs}"]), None)
                    log(f"[{out}]    boss: the movie stops shooting at row {t} with slot {bs} (type ${at[f'ty{bs}']:02x}) at "
                        f"{at[f'hp{bs}']} HP; repeating its last 48 rows the HP reaches 0 after {None if e_hp is None else e_hp - (t - c0)} more frames")
                    if e_hp is not None:
                        d = e_hp - (t - c0)
                        boss_cands = [("cyc", t, 48, nn) for nn in range(max(1, d - 12), d + 13)]
                        w0 = min(w0, c0)
        if boss_cands:
            cands = boss_cands
            drop_ck(w0)
            cname = checkpoint(w0)
        elif D - lg > 120:
            # no progress for a long time before failing: probably a boss that the movie expects to be dead.
            # Try repeating the movie's own attack rows somewhere after the place progress stopped.
            lo, hi = lg + 30, max(lg + 60, min(D - 6, lg + 700))
            w0 = min(w0, max(0, lo - 100))
            for _ in range(K * (1 + min(fails, 2))):
                t = rng.randrange(lo, hi)
                cands.append(("loop", t, rng.choice((24, 48, 48, 96)), rng.choice((1, 2, 2, 3, 4, 6))))
            drop_ck(w0)
            cname = checkpoint(w0)

        def trial(emu, ed):
            rr = apply_edit(rows, ed)
            return play(emu, cname, rr[w0:D + H + 2 + max(0, edit_cost(ed))], stall=stall)
        res = pool.map(trial, cands)
        scored = []
        for ed, x in zip(cands, res):
            surv = w0 + x.frames - edit_cost(ed)
            fin = x.reason in ("level", "end")
            scored.append(((1 if fin else 0, 0 if fin else x.progress, -surv if fin else surv), ed, x))
        scored.sort(key=lambda t: t[0], reverse=True)
        (fin, pg, _), ed, x = scored[0]
        surv = w0 + x.frames - edit_cost(ed)
        log(f"[{out}]    {r.reason} at {D} (progress {b_prog}); window {w0}..{D}; best of {len(cands)}: {ed} -> "
            f"{x.reason} at {w0 + x.frames} progress {x.progress}; others {[(w0 + y.frames, y.progress) for _, _, y in scored[1:5]]}")
        if fin or pg > b_prog or (pg == b_prog and surv > D + 40):
            rows = apply_edit(rows, ed)
            edits.append(ed)
            fails = 0
            save(False, 0)
        else:
            fails += 1
            if fails > 7:
                log(f"[{out}] giving up at {D}")
                save(False, 0)
                return False, rows, edits
    save(False, 0)
    return False, rows, edits
