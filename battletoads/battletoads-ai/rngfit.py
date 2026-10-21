"""Re-fit an old segment onto a new upstream route WITHOUT re-searching it (2026-10-02).

The later levels' old input lists stop working on a new route only where the game rolls its random numbers
(rngtest.py). The generator is scrambled in the main thread's idle loop (bank 0 $871F), so ANY change in CPU time
re-rolls it - and Select, which does nothing in play, changes the CPU time of its frame. So: replay the old inputs
from the new entry state and compare the toad's track (and chosen enemies') with the old run's own track
(replayed from the old bookmark). Where they part:

  0. lag?       busy scenes drop frames, and which frames drop depends on what the random objects are doing. A
                dropped frame here but not there only shifts the two runs in time: the old input for that frame is
                given again (or one is skipped). The frame counter $0B says whether the game logic ran.
  1. harmless?  play the old inputs on: if the tracks meet again within LOOK frames and stay together, keep going
  2. the tail?  within 300 frames of the end only the END state matters (a level change): idle until the state
                equals the old run's last frame
  2b. a wait:   (tried after the single-Select re-rolls) the old run waited and then pressed something: make that
                wait up to 130 frames longer or shorter - a platform that spawned a frame off after a fight
  3. re-roll:   go back up to W frames, add Select on one earlier frame, then two, then random patterns, and keep
                the first variant that tracks the old run for M more frames (each random decision is fixed on its
                own - a long window would need several lucky rolls at once)

    python rngfit.py <segment> <new entry bookmark> [out name]
        segment = logs/pbeam_<segment>.json (old inputs + old bookmark)
        env RNGFIT_IDS=7d,46   object ids tracked besides the toad (x, height, health)
            RNGFIT_BYTES=586   extra RAM bytes tracked (the Dark Queen's hit counter)
        -> logs/pbeam_<out>.json (bookmark = the new entry), bookmark <out>_end; prints every re-roll

A divergence nothing fixes is reported with bookmark <out>_stuck (W frames before it) and pbeam_<out>_partial.json.
"""
import json
import os
import random
import sys

from toads.emulator import BizHawk, LOGS_DIR

W = int(os.environ.get("RNGFIT_W", 180))
M = int(os.environ.get("RNGFIT_M", 12))
EVERY = 30
LOOK = 900
RANDOM_TRIES = int(os.environ.get("RNGFIT_RANDOM", 4000))
IDS = {int(v, 16) for v in os.environ.get("RNGFIT_IDS", "").split(",") if v}
BYTES = [int(v, 16) for v in os.environ.get("RNGFIT_BYTES", "").split(",") if v]


def key(m):
    k = (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x41B], m[0x475], m[0x51A], m[0x10])
    if IDS:                                                   # (sorted: the slot an object sits in may differ between the runs)
        k += tuple(sorted((m[0x3C1 + q], m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q]) for q in range(2, 15) if m[0x3C1 + q] in IDS))
    return k + tuple(m[a] for a in BYTES)


XTOL = int(os.environ.get("RNGFIT_XTOL", 0))                # the toad's x may differ by this much (a sub-pixel flicker after a stitched piece)


def same(a, b, loose=True):
    """the two keys agree: toad x within XTOL, a tracked object's x and height within 2*XTOL (its id and health exact),
    everything else exact"""
    if a == b:
        return True
    if loose and XTOL > 0:                                    # a dead body (health 0) lingering on one side is no difference
        a = a[:6] + tuple(u for u in a[6:] if not (isinstance(u, tuple) and u[3] == 0))
        b = b[:6] + tuple(u for u in b[6:] if not (isinstance(u, tuple) and u[3] == 0))
        if a == b:
            return True
    if not loose or XTOL == 0 or len(a) != len(b) or min(abs(a[0] - b[0]), 512 - abs(a[0] - b[0])) > XTOL or abs((a[1] - b[1] + 128) % 256 - 128) > XTOL or a[2] != b[2] or a[4:6] != b[4:6]:   # (z free: a bouncing platform)
        return False
    for u, v in zip(a[6:], b[6:]):
        if isinstance(u, tuple):
            if not (isinstance(v, tuple) and u[0] == v[0] and u[3] == v[3] and min(abs(u[1] - v[1]), 512 - abs(u[1] - v[1])) <= 2 * XTOL and abs(u[2] - v[2]) <= 2 * XTOL):
                return False
        elif u != v:
            return False
    return True


def key2(m):
    """every object on the list: used when two tracks meet again - a platform a frame off is not 'the same'"""
    return tuple((m[0x3C1 + q], m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q])


def btn(s):
    return tuple(v for v in s.replace(",", "+").split("+") if v)


class Fit:
    """the new run. `r` = index into the old inputs/track of the next frame to give; raw frames = len(out)"""

    def __init__(self, e, old, ref, tick, dref, ref2=None):
        self.e, self.old, self.ref, self.dref = e, old, ref, dref
        self.loose = [r is None for r in ref2] if ref2 else [False] * len(old)   # (a TAS-log stretch: tolerances apply there only)
        if os.environ.get("RNGFIT_LOOSEALL"):
            self.loose = [True] * len(old)
        n = len(old)
        # logic time: the frame counter $0B ticks only when the game logic ran. A short run of frames without a tick
        # is lag; there the pad is not read, so the next ticking frame's input stands in for it
        self.tick = tick
        self.nxt = [n] * (n + 1)                             # index of the next ticking frame at or after i
        for i in range(n - 1, -1, -1):
            self.nxt[i] = i if self.tick[i] else self.nxt[i + 1]
        self.lagf = [not self.tick[i] and self.nxt[i] < n and self.nxt[i] - i <= 3 and (i == 0 or self.tick[i - 1] or self.lagf_prev(i)) for i in range(n)]
        self.sel = set()                                     # old-input indices that get Select added
        self.sel2 = set()                                    # ... that get a second button (RNGFIT_BTN2, e.g. Down while standing)
        self.ins_at = {}                                     # old index -> idle frames put in before it (a longer wait)
        self.skip = set()                                    # old (idle) indices left out (a shorter wait)
        self.repl = {}                                       # old index -> button given instead (a one-frame tweak of OUR run only)
        self.insdone = {}
        self.lv = []                                         # level byte after every raw frame
        self.k2, self.cmp = None, None
        self.r = 0
        self.out = []
        self.saves = {}                                      # r -> (savestate, deaths, lives, tb, len(out))
        self.deaths = 0
        m = e.ram(0, 0x800)
        self.lives, self.tb = m[0x11], m[0x0B]
        self.lags = 0
        self.lagrun = 0

    def lagf_prev(self, i):
        j = i
        while j > 0 and not self.tick[j - 1]:
            j -= 1
        return i - j < 3

    def step(self):
        """one raw frame; True when the run is (still) on the old track"""
        e = self.e
        while self.r in self.skip:
            self.r += 1
        r = self.r
        n = len(self.old)
        if r % EVERY == 0 and r not in self.saves:           # (before any added wait at r, so that a rewind to r repeats it)
            self.saves[r] = (e.msave(), self.deaths, self.lives, self.tb, len(self.out))
        if self.insdone.get(r, 0) < self.ins_at.get(r, 0):   # an added wait: no old frame is used up
            self.insdone[r] = self.insdone.get(r, 0) + 1
            e.step((), 1)
            self.out.append("")
            m = e.ram(0, 0x800)
            if m[0x11] < self.lives:
                self.deaths += 1
            self.lives, self.tb = m[0x11], m[0x0B]
            self.lv.append(m[0x10])
            return True
        if r % EVERY == 0 and r not in self.saves:
            self.saves[r] = (e.msave(), self.deaths, self.lives, self.tb, len(self.out))
        def give(i):
            b = self.repl.get(i, self.old[i]) if i < n else ""
            if r in self.sel:
                b = (b + "+Select").lstrip("+")
            if r in self.sel2:
                b = (b + "+" + os.environ.get("RNGFIT_BTN2", "Down")).lstrip("+")
            e.step(btn(b), 1)
            return b, e.ram(0, 0x800)

        tb0 = self.tb
        j = r
        if r < n and self.lagf[r]:
            # the old run dropped this frame. If we drop it too, the same raw inputs are right (the pad is still
            # read). If we do not, this logic frame must get what the old run's next logic frame got
            sid = e.msave()
            b, m = give(r)
            if m[0x0B] != tb0:
                e.mload(sid)
                j = self.nxt[r]
                b, m = give(j)
                self.lags += 1
            e.mfree(sid)
        else:
            b, m = give(r)
        self.out.append(b)
        if m[0x11] < self.lives:
            self.deaths += 1
        self.lives = m[0x11]
        self.lv.append(m[0x10])
        k, tb = key(m), m[0x0B]
        self.k2, self.cmp = key2(m), None
        self.tb = tb
        if r >= n:
            self.r += 1
            return False
        ticked = tb != tb0
        if ticked:
            self.lagrun = 0
        if j != r or ticked == self.tick[r]:
            self.r = j + 1
            self.cmp = j
            return same(k, self.ref[j], self.loose[j]) and self.deaths == self.dref[j]
        if self.tick[r] and not ticked:                      # we dropped a frame the old run did not: give this input again
            self.lags += 1
            self.lagrun += 1
            if self.lagrun <= 6:
                return True
            self.r += 1                                      # not lag: the game stopped ticking (a transition the old run did not have)
            return False
        self.r += 1                                          # the old run stood still here for longer (no short lag)
        return False

    def rewind(self, to):
        s = max(f for f in self.saves if f <= to)
        self.drop_after(s)
        sid, self.deaths, self.lives, self.tb, n = self.saves[s]
        self.e.mload(sid)
        self.r = s
        del self.out[n:]
        del self.lv[n:]
        self.insdone = {j: c for j, c in self.insdone.items() if j < s}

    def drop_after(self, f0):
        for f in [f for f in self.saves if f > f0]:
            self.e.mfree(self.saves.pop(f)[0])

    def play(self, to):
        """returns the first old index where the tracks differ, or None"""
        while self.r < to:
            r = self.r
            if not self.step():
                return r
        return None


def reference(e, d, old, upto):
    """The track the new run is held to: the old inputs replayed from the old bookmark. A segment made of parts
    (virtual.py: old stretches and new pieces, each found from its own old state) is replayed part by part, each
    from its own bookmark - such a run never existed in one piece; the fit makes it exist.
    -> key per frame, all-objects key, 'the frame counter ticked', deaths so far, last RAM, deaths"""
    parts = d.get("parts") or [{"bookmark": d["bookmark"], "n": len(old)}]
    ref, ref2, tick, dref = [], [], [], []
    deaths, i, m = 0, 0, None
    for part in parts:
        if i >= upto:
            break
        if "tasrow" in part:                                  # a stretch of the TAS's own inputs: the reference is its FCEUX log
            import re
            rows = [l for l in open(part["taslog"]) if " x=" in l]
            pre = part.get("pre", 0)                           # idle frames put in first (their reference: the start row)
            for r in [part["tasrow"]] * pre + list(range(part["tasrow"] + 1, part["tasrow"] + 1 + part["n"] - pre)):
                l = rows[r]
                g = re.search(r"x=(\d+) h=(\d+) z=(\d+) st=\d+ an=\d+ hp=(\d+)", l)
                x, h, z, hp = (int(v) for v in g.groups())
                k = (x, h, 216, z, hp, int(part.get("level", 5)))
                objs = re.findall(r"([0-9a-f]{2}):(\d+),(\d+),(\d+),(\d+)", l)
                if IDS:
                    k += tuple(sorted((int(a, 16), int(ox), int(oh), int(ohp)) for a, ox, oh, ohp, _ in objs if int(a, 16) in IDS))
                k += tuple(0 for _ in BYTES)
                ref.append(k)
                ref2.append(None)                           # (the log has no 16-bit heights: no strict object check here)
                tick.append(True)
                dref.append(deaths)
            i += part["n"]
            m = None
            continue
        e.load(part["bookmark"])
        lives, tb = e.byte(0x11), e.byte(0x0B)
        pre = part.get("pre", 0)                              # idle frames put in first (a wait inserted in the NEW run only):
        m = e.ram(0, 0x800)                                   # their reference is the standing state at the bookmark
        for _ in range(min(pre, max(0, upto - i))):
            ref.append(key(m)); ref2.append(key2(m)); tick.append(True); dref.append(deaths)
        src = [x.replace(",", "+") for x in part["inputs"]] if part.get("inputs") else old[i:i + part["n"]]   # a part may carry its own reference inputs (ours differ by a tweak)
        for b in src[pre:min(upto, i + part["n"]) - i]:
            e.step(btn(b), 1)
            m = e.ram(0, 0x800)
            deaths += m[0x11] < lives
            lives = m[0x11]
            ref.append(key(m))
            ref2.append(key2(m))
            tick.append(m[0x0B] != tb)
            tb = m[0x0B]
            dref.append(deaths)
        i += part["n"]
    return ref, ref2, tick, dref, m, deaths


def main(seg, entry, out=None):
    out = out or seg + "f"
    d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    old = [b.replace(",", "+") for b in d["inputs"]]
    e = BizHawk(log_name=f"rngfit_{seg}.log")
    ref, ref2, tick, dref, m, deaths = reference(e, d, old, len(old))   # the old run's own track
    n = len(old)
    if m is None:
        m = e.ram(0, 0x800)
    tend = (m[0x0B], m[0x0C])                                  # the old run's timers at its last frame
    m_end = bytes(m)
    print(seg, "old track:", n, "frames, ends", ref[-1], "timers", tend, "deaths", deaths, flush=True)

    e.load(entry)
    F = Fit(e, old, ref, tick, dref, ref2)
    F.sel = {int(v) for v in os.environ.get("RNGFIT_SEL", "").split(",") if v}   # re-rolls already found (resume)
    F.sel2 = {int(v) for v in os.environ.get("RNGFIT_SEL2", "").split(",") if v}
    if int(os.environ.get("RNGFIT_ENTRYWAIT", 0)):             # the entry is the frame the toad is set down: idle this long first
        F.ins_at[0] = int(os.environ["RNGFIT_ENTRYWAIT"])
    rerolls, safe = [(0, tuple(sorted(F.sel)), 0)] if F.sel else [], 0
    while True:
        bad = F.play(n)
        if bad is None:
            break
        lo = max(0, bad - W)
        # 1. harmless? do the tracks meet again and stay together
        run, run2, back = 0, 0, None
        while F.r < min(n, bad + LOOK):
            ok = F.step()
            run = run + 1 if ok else 0
            run2 = run2 + 1 if ok and (F.cmp is None or ref2[F.cmp] is None or F.k2 == ref2[F.cmp]) else 0
            if run >= 60:
                back = F.r - 60
                break
        lenient = None
        if back is not None and run2 >= 60:
            print(f"  frame {bad}: tracks differ, meet again at {back} (old inputs kept)", flush=True)
            safe = F.r
            continue
        if back is not None:                                  # the toad is back on its track but other objects are not where they were
            lenient = F.r
        # 2. the tail: only the end state matters
        if bad >= n - 300 and lenient is None:
            F.rewind(lo)
            hit = False
            for _ in range(n - lo + 300):
                F.step()
                if F.r > bad - 30 and key(e.ram(0, 0x800)) == ref[-1]:
                    hit = True
                    break
            if hit:
                print(f"  frame {bad}: the level change comes at another frame; segment is now {len(F.out)} frames (was {n})", flush=True)
                break
        # 3. re-roll with Select
        base = set(F.sel)
        bounds = []
        if d.get("parts"):
            q = 0
            for part in d["parts"]:
                q += part["n"]
                bounds.append(q)
        cands = [(j,) for j in range(bad - 1, lo - 1, -1) if j not in base]
        cands += [(j, j2) for j in range(bad - 1, lo - 1, -3) for j2 in range(j - 1, max(lo, j - 40) - 1, -2)
                  if j not in base and j2 not in base]
        rnd = random.Random(bad)
        free = [j for j in range(max(lo, safe), bad) if j not in base]
        wide = [j for j in range(lo, bad) if j not in base]
        for t in range(RANDOM_TRIES):
            pool = free if (t < RANDOM_TRIES // 2 and len(free) >= 4) else wide
            c = tuple(sorted(j for j in pool if rnd.random() < 0.5))
            if c:
                cands.append(c)
        fixed = False
        nsingle = sum(1 for c in cands if len(c) == 1)

        def reroll(group, first):
            for tries, c in enumerate(group, first):
                F.sel = base | set(c)
                F.rewind(min(c))
                b2 = F.play(min(n, bad + M))
                if b2 is None or b2 >= bad + M:
                    rerolls.append((bad, c, tries))
                    print(f"  frame {bad}: old track lost -> Select on {c if len(c) < 4 else str(len(c)) + ' frames'} ({tries} tries) holds to {F.r}", flush=True)
                    return True
                F.drop_after(min(c))                          # savestates taken under a rejected variant must not be reused
            F.sel = base
            return False

        def shift():
            """the old run waited (hanging, standing) and then pressed something at p: wait a little longer or shorter.
            Platforms that spawn with the camera can sit a frame or two off after a fight went differently."""
            q = bad - 1
            while q > lo and not old[q]:
                q -= 1
            p = q
            while p > lo and (old[p - 1] or any(old[max(lo, p - 8):p])):
                p -= 1
            spots = [p] if old[p] else []
            spots += [q for q in bounds if lo <= q < bad and q not in spots]   # a stitched piece's end: wait there too
            # any short idle stretch (>= 2 frames) before the divergence: a bouncing platform (period 39) or a
            # disappearing one can be re-phased by standing a little longer there (tried after the main spot)
            idles = [q for q in range(bad - 2, lo + 1, -1) if not old[q] and not old[q - 1] and old[q + 1]]
            extra = [q + 1 for q in idles if q + 1 not in spots][:6]
            if not spots and not extra:
                return False
            tries = [(p, v) for p in spots for a in range(1, 131) for v in (-a, a)]
            tries += [(p, a) for p in extra for a in range(1, 46)]
            for p, k in tries:
                if k < 0 and (p + k < 0 or any(old[p + k:p]) or any(j in base for j in range(p + k, p))):
                    continue
                i0, s0 = dict(F.ins_at), set(F.skip)
                F.rewind(max(0, p + min(k, 0)))
                if k > 0:
                    F.ins_at[p] = F.ins_at.get(p, 0) + k
                else:
                    F.skip |= set(range(p + k, p))
                b2 = F.play(min(n, bad + 45))
                if b2 is None or b2 >= bad + 45:
                    rerolls.append((bad, ("wait", p, k), 0))
                    print(f"  frame {bad}: old track lost -> the wait before frame {p} made {abs(k)} frame(s) {'longer' if k > 0 else 'shorter'}; holds to {F.r}", flush=True)
                    return True
                F.ins_at, F.skip = i0, s0
                F.drop_after(max(0, p + min(k, 0)))
            return False

        def tweak():
            """a one-frame button replacement in OUR run (the reference stays): a pixel of drift at a platform edge, a
            tap that landed a frame off"""
            TB = ["", "A", "Right", "Right+A", "Left", "Left+A", "B", "Down"]
            for p in range(bad - 1, max(lo, bad - 130) - 1, -1):
                if p in F.repl:
                    continue
                for b in TB:
                    if b == old[p]:
                        continue
                    F.repl[p] = b
                    F.rewind(p)
                    b2 = F.play(min(n, bad + M))
                    if b2 is None or b2 >= bad + M:
                        rerolls.append((bad, ("tweak", p, b), 0))
                        print(f"  frame {bad}: old track lost -> frame {p} given {b!r} instead of {old[p]!r}; holds to {F.r}", flush=True)
                        return True
                    del F.repl[p]
                    F.drop_after(p)
            return False

        at_join = any(0 <= bad - q <= 12 for q in bounds)      # a stitched piece that does not join: no amount of dice will fix it
        fixed = reroll(cands[:nsingle], 1) or shift() or tweak() or reroll(cands[nsingle:nsingle + (0 if at_join else 900 if lenient is not None else len(cands))], nsingle + 1)
        if not fixed and os.environ.get("RNGFIT_BTN2"):       # the second button: singles and pairs on frames where the old input is idle
            base2 = set(F.sel2)
            idle = [j for j in range(bad - 1, lo - 1, -1) if not old[j] and j not in base2]
            c2 = [(j,) for j in idle] + [(j, j2) for j in idle[::2] for j2 in idle if j2 < j][:1500]
            for tries, c in enumerate(c2, 1):
                F.sel = base
                F.sel2 = base2 | set(c)
                F.rewind(min(c))
                b2 = F.play(min(n, bad + M))
                if b2 is None or b2 >= bad + M:
                    rerolls.append((bad, ("btn2", c), tries))
                    print(f"  frame {bad}: old track lost -> {os.environ['RNGFIT_BTN2']} on {c} ({tries} tries) holds to {F.r}", flush=True)
                    fixed = True
                    break
                F.drop_after(min(c))
            if not fixed:
                F.sel2 = base2
        if fixed:
            safe = F.r
        elif lenient is not None:                             # nothing reproduces it: go on with the toad's track alone
            F.sel = base
            F.rewind(lo)
            while F.r < lenient:
                F.step()
            safe = F.r
            fixed = True
            print(f"  frame {bad}: tracks differ and meet again at {back}, but other objects are placed differently and no re-roll restores them (old inputs kept)", flush=True)
        if not fixed:
            F.sel = base
            F.rewind(lo)
            e.save(out + "_stuck")
            print(f"STUCK at frame {bad} of {n}: {len(cands)} re-rolls tried; old key {ref[bad]}; bookmark {out}_stuck = old frame {F.r}", flush=True)
            json.dump({"bookmark": entry, "inputs": F.out, "stuck_at": bad}, open(LOGS_DIR / f"pbeam_{out}_partial.json", "w"))
            e.close()
            return False
    # 4. the briefing page: the old segments pressed Start now and then and waited ~220 frames on the "LEVEL n" page.
    #    Mashing A (a fresh press every other frame) from just before the level byte changes skips it at once.
    fin = list(F.out)
    lv = list(F.lv)
    slack = 0
    chg = [i for i in range(max(1, len(lv) - 900), len(lv)) if lv[i] != lv[i - 1]]
    if chg and os.environ.get("RNGFIT_MASH", "1") != "0":
        c = chg[-1]
        pats = {"A even": ("A", ""), "A odd": ("", "A"), "B even": ("B", ""), "B odd": ("", "B")}   # (a Start press that lands in the new level pauses it)

        def goto(raw):
            """the new run's own inputs again, up to raw frame `raw`"""
            F.rewind(max(f for f, sv in F.saves.items() if sv[4] <= raw))
            for b in fin[len(F.out):raw]:
                e.step(btn(b), 1)
                F.out.append(b)

        def mash(back, pat):
            """-> (frames to the key match, idle frames from there to the old run's timers, entry identical?)"""
            goto(max(0, c - back))
            for k in range(len(fin) - (c - back) + 60):
                b = pat[k % len(pat)]
                e.step(btn(b), 1)
                F.out.append(b)
                if same(key(e.ram(0, 0x800)), ref[-1]):
                    # the level has only just been set up (timers ~1). The old run's last frame is the same picture
                    # later (timers 34 after a warp, ~215 behind a briefing page): idle on to that frame to compare
                    here = e.msave()
                    res = (len(F.out), 60, False)                 # (no such frame: the level's clock is not what the old run waited on)
                    for w in range(400):
                        m2 = e.ram(0, 0x800)
                        if (m2[0x0B], m2[0x0C]) == tend and key(m2) == ref[-1]:
                            res = (len(F.out), w, sum(1 for i in range(0x800) if m2[i] != m_end[i]) == 0)
                            break
                        e.step((), 1)
                    e.mload(here)
                    e.mfree(here)
                    return res
            return None

        best = None
        for back in (120, 60, 30, 0):
            for name, pat in pats.items():
                got = mash(back, pat)
                if got and (best is None or (got[0], not got[2]) < (best[0][0], not best[0][2])):
                    best = (got, back, name)
        if best and best[0][0] < len(fin):
            slack = mash(best[1], pats[best[2]])[1]
            print(f"  briefing page: '{best[2]}' from frame {c - best[1]} -> the toad is set down at frame {len(F.out)} (was {len(fin)}); the old run's "
                  f"entry frame is {slack} idle frames later and is {'identical' if best[0][2] else 'not identical (the sound engine is at another point: the dice differ)'}", flush=True)
        else:
            goto(len(fin))
    # the segment ends where the toad is set down (<out>_end0); <out>_end is the old run's entry frame, `slack` idle
    # frames later. The next segment decides how many of those it needs (RNGFIT_ENTRYWAIT, entryscan)
    e.save(out + "_end0")
    m = e.ram(0, 0x800)
    json.dump({"bookmark": entry, "inputs": F.out, "note": d.get("note", ""), "rerolls": rerolls, "slack": slack}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
    print(f"{seg} -> pbeam_{out}.json: {len(F.out)} frames, {len(rerolls)} re-rolls, {F.lags} lag shifts; end level {m[0x10]} toad {m[0x3FD] | m[0x3EE] << 8},{m[0x439]} hp {m[0x51A]} lives {m[0x11]}; slack {slack}", flush=True)
    e.step((), slack) if slack else None
    e.save(out + "_end")
    e.close()
    return True


def scan(seg, entry0, slack):
    """The entry bookmark is the frame the toad is set down; the old run started `slack` idle frames later (it sat on
    the briefing page while the level's clock ran). How few idle frames does this segment need? For k = 0.. the old
    inputs are replayed after k idle frames; d(k) = how far the old track holds. The full slack is the reference;
    the smallest k that gets as far is the answer (prints 'SCAN k=<k>')."""
    slack = int(slack)
    d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    old = [b.replace(",", "+") for b in d["inputs"]]
    e = BizHawk(log_name=f"rngscan_{seg}.log")
    cap = min(len(old), int(os.environ.get("RNGFIT_SCANCAP", 6000)))
    ref, ref2, tick, dref, m, deaths = reference(e, d, old, cap)

    def reach(k):
        e.load(entry0)
        F = Fit(e, old[:cap], ref, tick, dref)
        F.ins_at[0] = k
        bad = F.play(cap)
        F.drop_after(-1)
        return cap if bad is None else bad

    full = reach(slack)
    print(f"{seg}: with the full {slack} idle frames the old track holds to {full}", flush=True)
    best, far = slack, full
    for k in range(0, min(slack, 61)):                       # either the level needs the old phase exactly, or hardly any wait at all
        got = reach(k)
        if got > far or (got == far and k < best):            # as far with less waiting
            best, far = k, got
            print(f"  k={k}: holds to {got}", flush=True)
    print(f"SCAN k={best}", flush=True)
    e.close()
    return best


if __name__ == "__main__":
    if sys.argv[1] == "--scan":
        scan(*sys.argv[2:])
        sys.exit(0)
    ok = main(*sys.argv[1:])
    sys.exit(0 if ok else 1)
