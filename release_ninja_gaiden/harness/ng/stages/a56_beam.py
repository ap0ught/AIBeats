"""Acts 5-6: TAS-guided legal beam search for one stage (one EmuHawk).

Every row played goes through a56_common.Enforcer, so every node's input list is legal by construction (L+R/U+D
never emitted; per-button period 5 / hold 2 / release 2 / windows). Score = TAS progress: the largest
k - dist/1.5 over TAS frames k of the same stage and room near the node's TAS pointer, where dist is |dx| + |dy|
between Ryu and the TAS's Ryu at frame k. Nodes that die are dropped; nodes are deduplicated by RAM hash + the
enforcer's button state. The search ends when nodes reach the next stage ($6D change = "load"); the earliest
load frame wins (ties: higher HP / ninpo / same item as the TAS).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a56_common as C  # noqa: E402

from ng.mode import TICKS  # noqa: E402

BOSS_MACRO = [
    # legal slash cancel (measured at Jaquio): Down, Down+B, then B WITHOUT Down cancels the slash, so a new slash
    # (and a new hit) every 5 frames
    ("R", ("Down",), ("Down", "B"), ("B",), (), ()),
    ("R", ("Down", "Left"), ("Down", "Left", "B"), ("Left", "B"), ("Left",), ("Left",)),
    ("R", ("Down", "Right"), ("Down", "Right", "B"), ("Right", "B"), ("Right",), ("Right",)),
    ("R", ("Down",), ("Down", "B"), ("B", "Left"), ("Left",), ("Left",)),
    ("R", ("Down",), ("Down", "B"), ("B", "Right"), ("Right",), ("Right",)),
    ("Right",), ("Left",), (), ("Right", "A"), ("Left", "A"), ("A",), ("Up", "B"),
]
DIRS_MACRO = [
    ("Right",), ("Left",), (), ("Right", "A"), ("Left", "A"), ("A",), ("Right", "B"), ("Left", "B"), ("B",),
]


def macro_rows(m, n):
    """A macro = buttons held for n frames; A/B only on the first 2 frames (a press, then released).
    m may carry an offset: ("@3", "Right", "A") = the direction from frame 0, the A/B press from frame 3.
    m may be a split: ("|", "Right", "Left") = first half Right, second half Left."""
    if m and m[0] == "R":                       # explicit rows (padded / cut to n)
        rows = [tuple(r) for r in m[1:]]
        return (rows + [rows[-1]] * n)[:n]
    if m and m[0] == "^":                       # ("^", d1, d2, k): d1+A for 2 frames, d1 until k, then d2
        _, d1, d2, k = m
        return [(d1, "A")] * 2 + [(d1,)] * (k - 2) + [(d2,)] * (n - k)
    if m and m[0] == "|":
        h = n // 2
        return [(m[1],) if m[1] else ()] * h + [(m[2],) if m[2] else ()] * (n - h)
    off = 0
    if m and str(m[0]).startswith("@"):
        off = int(m[0][1:])
        m = m[1:]
    d = tuple(b for b in m if b not in ("A", "B"))
    p = tuple(b for b in m if b in ("A", "B"))
    return [d + p if off <= i < off + 2 else d for i in range(n)]


MACROS8 = [
    ("Right",), ("Left",), (),
    ("Right", "A"), ("@4", "Right", "A"), ("Left", "A"), ("@4", "Left", "A"),
    ("Right", "B"), ("Left", "B"), ("Down", "B"),
    ("|", "Right", "Left"), ("|", "Left", "Right"),
    ("^", "Left", "Right", 2), ("^", "Right", "Left", 2), ("^", "Left", "Right", 4), ("^", "Right", "Left", 4),
]


def node_hp_floor(s):
    return s["hp"]          # placeholder: lazy following accepts our own HP whatever it is (deaths are caught)


class Node:
    __slots__ = ("sid", "en", "rows", "f", "st", "score", "k", "done", "hist")

    def __init__(self, sid, en, rows, f, st, score, k, done=None):
        self.sid, self.en, self.rows, self.f, self.st, self.score, self.k, self.done = sid, en, rows, f, st, score, k, done


class StageBeam:
    def __init__(self, e, stage, start_state, history=(), width=8, chunk=4, tas_offsets=(0, 1),
                 macros=DIRS_MACRO, log=None, hp_weight=2.0, ninpo_weight=0.5, item_weight=40.0, max_frames=None,
                 extra_score=None, tas_k0=None, boss=False, boss_w=8.0, ref=None):
        self.e, self.stage, self.width, self.chunk = e, stage, width, chunk
        self.tas_offsets, self.macros = tas_offsets, macros
        if ref is None:
            ref = C.tas_ref(stage)
        self.ref = ref
        self.T, self.R = ref["trace"], ref["rows"]
        self.tas_control = ref["control"]
        self.tas_load_next = ref["load_next"]
        self.hp_w, self.np_w, self.it_w = hp_weight, ninpo_weight, item_weight
        self.extra_score = extra_score
        self.boss, self.boss_w = boss, boss_w
        self.post_steps = 8 if boss else 0
        self.diverse, self.per_bucket = True, 1
        self.lazy, self.lazy_steps = True, 0
        import os
        self.explore_budget, self.stuck_steps = (1500 if (not boss or os.environ.get("A56_BOSS_EXPLORE")) else 0), 10
        self.lazy_tol = 3          # px (|dx|+|dy|) from the reference that still counts as "on the reference"
        self.dump = C.PROJECT / "states" / "tmp" / f"a56_best_{C.NAMES[stage]}.inputs.txt"
        if boss:
            self.macros = BOSS_MACRO if macros is DIRS_MACRO else macros
        self.boss_pos_w = 0.15     # boss stages: frames per px away from the reference's position at the same time
        self.px_w = 0.75          # frames per pixel off the reference path in x (> 1/1.5: nearest point wins)
        self.py_w = 0.5           # ... in y
        if chunk >= 8 and macros is DIRS_MACRO and not boss:
            self.macros = MACROS8
        self.log = log or (lambda *a: print(*a, flush=True))
        e.tick(TICKS)
        st = e.load(start_state) if isinstance(start_state, str) else start_state
        self.f0 = st["frame"]
        self.max_frames = max_frames or (int((self.tas_load_next - self.tas_control) * 1.5) + (1500 if boss else 200))
        en = C.Enforcer(history)
        # reference frames of this stage by room
        self.by_room = {}
        for k in range(self.tas_control, self.tas_load_next):
            t = self.T[k]
            if t is None:
                continue
            self.by_room.setdefault(t["room"], []).append((k, C.abs_x(t), t["y"]))
        k0 = tas_k0 if tas_k0 is not None else self.tas_control
        if tas_k0 is None and st.get("room") in self.by_room and                 (C.abs_x(st), st["y"]) != (C.abs_x(self.T[self.tas_control]), self.T[self.tas_control]["y"]):
            lst = self.by_room[st["room"]]
            k0 = min(lst, key=lambda p: abs(p[1] - C.abs_x(st)) + abs(p[2] - st["y"]))[0]
        sid = e.msave()
        self.root = Node(sid, en, [], self.f0, st, 0.0, k0)
        self.k_off = k0 - self.f0
        self.ref_boss0 = next((k for k in range(self.tas_control, self.tas_load_next)
                               if self.T[k] is not None and self.T[k].get("bosshp", 1) == 0), self.tas_load_next)
        self.boss_pos_cut = 0
        self.kill_cache = {}
        self._cs_seen = False
        self.bdist_w = 0.1 if stage == 20 else 0.0   # Jaquio only: frames per px from the hitting spot
        self.evals = 0

    # ---------------------------------------------------------------------------------------------------------
    def progress(self, st, kprev):
        if self.boss:
            # boss fights: follow the reference in TIME (its position at the same fight frame), hits count separately
            k = min(max(st["frame"] + self.k_off, self.tas_control), self.tas_load_next - 1)
            t = self.T[k]
            if t is None or k >= self.ref_boss0 - self.boss_pos_cut:
                return float(k), k        # the reference has (nearly) killed the boss: its position means nothing
            return k - (abs(C.abs_x(st) - C.abs_x(t)) + abs(st["y"] - t["y"])) * self.boss_pos_w, k
        lst = self.by_room.get(st["room"])
        if not lst:
            return kprev - 50.0, kprev
        ax, y = C.abs_x(st), st["y"]
        best, bk = -1e9, kprev
        lo, hi = kprev - 60, kprev + 60
        cand = [p for p in lst if lo <= p[0] <= hi] or lst
        # slope 2 frames per pixel (> 1/1.5): along a straight TAS run the nearest TAS point wins
        for k, tx, ty in cand:
            if self.boss:
                v = k - (abs(ax - tx) + abs(y - ty)) * self.boss_pos_w
            else:
                v = k - abs(ax - tx) * self.px_w - abs(y - ty) * self.py_w
            if v > best:
                best, bk = v, k
        return best, bk

    def score(self, st, k):
        t = self.T[min(max(k, self.tas_control), self.tas_load_next - 1)]
        sc = 0.0
        sc -= self.hp_w * max(0, t["hp"] - st["hp"])
        sc -= self.np_w * max(0, t["ninpo"] - st["ninpo"])
        if t["item"] != st["item"]:
            sc -= self.it_w
        if self.boss and "bsum" in st:
            sc -= self.boss_w * st["bsum"]
        elif self.boss:
            sc -= self.boss_w * (st["bosshp"] - t["bosshp"])
            if "bx" in st and st["bosshp"] > 0 and self.bdist_w:
                # Jaquio (measured from the TAS's hits): sword hits with Jaquio ~45 px to the right, ~18 px higher
                sc -= self.bdist_w * (abs((st["bx"] - st["x"]) - 45) + abs((st["y"] - st["by"]) - 18))
        if self.extra_score:
            sc += self.extra_score(self, st, k)
        return sc

    # ---------------------------------------------------------------------------------------------------------
    def candidates(self, node):
        out = []
        n = self.chunk
        for o in self.tas_offsets:
            a = node.k + o
            if a < 0:
                continue
            out.append(("tas%+d" % o, [tuple(r) for r in self.R[a:a + n]] + [()] * max(0, n - len(self.R[a:a + n]))))
        for m in self.macros:
            out.append(("m" + "+".join(str(x) for x in m), macro_rows(m, n)))
        return out

    def is_on(self, node):
        """the node sits exactly on the reference path (same x, subpixel, y as the reference at its pointer)"""
        k = node.k
        if not (self.tas_control <= k < self.tas_load_next):
            return False
        t = self.T[k]
        if t is None:
            return False
        s = node.st
        if self.lazy_tol == 0:
            return (C.abs_x(s) == C.abs_x(t) and s["y"] == t["y"] and s.get("xsub") == t.get("xsub")
                    and s["room"] == t["room"] and s["hp"] >= t["hp"])
        return (abs(C.abs_x(s) - C.abs_x(t)) + abs(s["y"] - t["y"]) <= self.lazy_tol and s["room"] == t["room"]
                and s["hp"] >= min(t["hp"], node_hp_floor(s)))

    def expand(self, node, only=None, cands=None):
        e = self.e
        kids = []
        for tag, want in (cands if cands is not None else self.candidates(node)):
            if only and tag not in only:
                continue
            en = node.en.copy()
            rows = [en.emit(w) for w in want]
            e.mload(node.sid)
            e.run(rows)
            tr = e.last_trace
            self.evals += 1
            dead = any(s.get("dw") or s.get("hp", 1) == 0 or s.get("hp", 1) > 16 or s.get("dead", 0) & 0x80 for s in tr) and \
                not any(s["stage"] != self.stage for s in tr)
            if dead:
                continue
            last = tr[-1]
            done = next((s["frame"] for s in tr if s["stage"] != self.stage), None)
            if (not self.boss) and done is None and any(s.get("cs") or s.get("se") for s in tr):
                key = ("se", last["frame"], last["timer"], last["subtimer"], last["ninpo"], last["hp"])
                if key in self.kill_cache:
                    done, extra, last = self.kill_cache[key]
                    rows = rows + [en.emit(r) for r in extra]
                else:
                    self._cs_seen = any(s.get("cs") for s in tr)
                    done, extra = self.to_next_stage(en)
                    e.trace(True)
                    rows = rows + extra
                    last = self.e.state()
                    self.kill_cache[key] = (done, list(extra), last)
            if self.boss and done is None and any(s["bosshp"] == 0 for s in tr):
                kf = next(s["frame"] for s in tr if s["bosshp"] == 0)
                key = (kf, last["frame"], last["timer"], last["subtimer"], last["ninpo"])
                if key in self.kill_cache:
                    done, extra, last = self.kill_cache[key]
                    rows = rows + [en.emit(r) for r in extra]
                else:
                    e.trace(False)
                    done, extra = self.finish_boss(en)
                    e.trace(True)
                    rows = rows + extra
                    last = self.e.state()
                    self.kill_cache[key] = (done, list(extra), last)
            ram = e.ram_all()
            if self.boss:
                last = dict(last)
                last["bx"], last["by"] = ram[0x467], ram[0x487]
                if self.stage == 21:
                    # the demon: slot 6 (16 HP, hit first) then slot 7 (the heart, shown in $66)
                    last["bsum"] = (ram[0x496] if ram[0x496] < 0x80 else 0) + (ram[0x497] if ram[0x497] < 0x80 else 0)
            sig = hashlib.sha1(ram + repr(sorted((b, en.held[b], min(en.run[b], 6)) for b in C.BTNS)).encode()).digest()
            sid = e.msave()
            prog, k = self.progress(last, node.k) if done is None else (1e6 - done, node.k)
            sc = prog + (self.score(last, k) if done is None else 0)
            kid = Node(sid, en, node.rows + rows, last["frame"], last, sc, k, done)
            kid.hist = sig
            kids.append(kid)
        return kids

    def explore(self, seeds, budget, target_score):
        """Go-explore around an obstacle: archive of cells (room, x/8, y/8) -> earliest node; expand random macros
        from rarely chosen cells until a node scores above target_score (or the stage ends). Returns [node] or None."""
        import random
        rnd = random.Random(seeds[0].f * 31 + len(seeds))
        arch, chosen = {}, {}
        e = self.e

        def cell(n):
            s = n.st
            return (s["room"], C.abs_x(s) // 8, s["y"] // 8)

        for sd in seeds:
            if sd.sid is None:
                continue
            e.mload(sd.sid)
            n2 = Node(e.msave(), sd.en.copy(), list(sd.rows), sd.f, sd.st, sd.score, sd.k)
            n2.hist = sd.hist
            c = cell(n2)
            if c in arch:
                e.mfree(arch[c].sid)
            arch[c] = n2
        macros = list(self.macros) + list(MACROS8)
        best = None
        try:
            for it in range(budget):
                cells = list(arch)
                if not cells:
                    return None
                w = [1.0 / (1 + chosen.get(c, 0)) ** 0.5 * (1.0 + max(0.0, arch[c].score - target_score + 40) / 40)
                     for c in cells]
                c = rnd.choices(cells, weights=w)[0]
                chosen[c] = chosen.get(c, 0) + 1
                nd = arch[c]
                m = rnd.choice(macros)
                kids = self.expand(nd, cands=[("x", macro_rows(m, self.chunk))])
                for kd in kids:
                    if kd.done is not None:
                        kd.sid and e.mfree(kd.sid)
                        kd.sid = None
                        return [kd]
                    if kd.score > target_score and (best is None or kd.score - kd.f > best.score - best.f):
                        if best is not None and best.sid is not None:
                            e.mfree(best.sid)
                        best = kd
                        continue
                    c2 = cell(kd)
                    if c2 not in arch or kd.f < arch[c2].f:
                        if c2 in arch:
                            e.mfree(arch[c2].sid)
                        arch[c2] = kd
                    else:
                        e.mfree(kd.sid)
                if best is not None and it > budget // 4:
                    break
            if best is None:
                return None
            self.log(f"[{C.NAMES[self.stage]}] explore: past the obstacle at f {best.f} (score {best.score:.1f} > "
                     f"{target_score:.1f}) after {it + 1} expansions, {len(arch)} cells")
            return [best]
        finally:
            for n in arch.values():
                if n.sid is not None and n is not best:
                    e.mfree(n.sid)

    def select(self, kids):
        """Top `width` by score, but at most `per_bucket` per (room, x/8, y/16, hp) bucket in the first pass."""
        if not self.diverse:
            return kids[:self.width]
        out, cnt, rest = [], {}, []
        for k in kids:
            s = k.st
            key = (s["room"], C.abs_x(s) // 8, s["y"] // 16, s["hp"], s.get("bosshp", 0))
            if cnt.get(key, 0) < self.per_bucket and len(out) < self.width:
                cnt[key] = cnt.get(key, 0) + 1
                out.append(k)
            else:
                rest.append(k)
        for k in rest:
            if len(out) >= self.width:
                break
            out.append(k)
        out.sort(key=lambda n: -n.score)
        return out

    def to_next_stage(self, en):
        """Play on (tally, stage-end walk) with nothing held; when the cinematic engine runs, skip it with one Start
        press (held 2 frames, retried every 5 frames until the script-end code runs); then wait for the next stage's
        load. Returns (load frame, rows)."""
        e = self.e
        e.trace(True)
        rows, pressed_at, skipped = [], None, False
        try:
            for i in range(8000):
                want = ()
                if not skipped and self._cs_seen and (pressed_at is None or i - pressed_at >= 5):
                    if en.can_press("Start"):
                        want = ("Start",)
                        pressed_at = i
                r = en.emit(want)
                rows.append(r)
                tr = e.run([r])
                st = e.last_trace[-1] if e.last_trace else tr
                if st["stage"] != self.stage:
                    return st["frame"], rows
                if st.get("cs"):
                    self._cs_seen = True
                if st.get("csskip") and (st.get("pad", 0) & 0x10):
                    skipped = True
                if skipped:
                    n, st = e.until(0x6D, "ne", self.stage, 400)
                    rows += [en.emit(()) for _ in range(n)]
                    return st["frame"], rows
            return e.state()["frame"] + 10000, rows
        finally:
            self._cs_seen = False

    def finish_boss(self, en):
        """The boss is dead: play nothing until the next stage loads (6-5: until END seen). Returns (frame, rows)."""
        e = self.e
        if self.stage < 21:
            return self.to_next_stage(en)
        n, st = e.until(0x63, "eq", 0, 3000)          # P: first tally frame with timer 0
        rows = [en.emit(()) for _ in range(n)]
        p = st["frame"]
        while True:                                     # E: first frame > P with $3E == 1; END seen = E + 1
            st = e.step((), 1)
            rows.append(en.emit(()))
            if st["hudphase"] == 1:
                break
        self.end_info = {"P": p, "E": st["frame"]}
        return st["frame"] + 1, rows

    def run(self, max_steps=100000, deadline=None):
        from collections import deque
        beam = [self.root]
        self.root.hist = b""
        pool, first_done_step = [], None
        step = 0
        t0 = time.time()
        gens = deque([beam])          # recent generations (their states stay alive for backtracking)
        G = 10
        boost_until, backtracks, last_bt_frame = 0, 0, -1
        hist_best = []
        base_width = self.width

        self.checkpoints = []

        def push_gen(b):
            if step % 10 == 0 and b and b[0].sid is not None:
                nd = b[0]
                self.e.mload(nd.sid)
                cp = Node(self.e.msave(), nd.en.copy(), list(nd.rows), nd.f, nd.st, nd.score, nd.k)
                cp.hist = nd.hist
                self.checkpoints.append(cp)
                if len(self.checkpoints) > 40:
                    old = self.checkpoints.pop(0)
                    self.e.mfree(old.sid)
            gens.append(b)
            while len(gens) > G:
                for nd in gens.popleft():
                    if nd.sid is not None:
                        self.e.mfree(nd.sid)
                        nd.sid = None

        self.e.trace(True)
        while step < max_steps:
            step += 1
            self.width = base_width * 2 if step <= boost_until else base_width
            top = beam[0]
            if self.lazy and step > boost_until and self.is_on(top):
                ks = self.expand(top, only=("tas+0",))
                if len(ks) == 1 and ks[0].done is None and self.is_on(ks[0]) and                         abs(ks[0].k - (top.k + self.chunk)) <= (1 if self.lazy_tol else 0):
                    beam = ks
                    push_gen(beam)
                    self.lazy_steps += 1
                    if step % 10 == 0:
                        self.log(f"[{C.NAMES[self.stage]}] step {step} f {ks[0].f} following the reference (k {ks[0].k}) "
                                 f"lazy {self.lazy_steps} evals {self.evals}")
                    continue
                for kd in ks:
                    self.e.mfree(kd.sid)
            kids = []
            for nd in beam:
                kids.extend(self.expand(nd))
            seen = {}
            for kd in kids:
                if kd.hist in seen and seen[kd.hist].score >= kd.score:
                    self.e.mfree(kd.sid)
                    continue
                if kd.hist in seen:
                    self.e.mfree(seen[kd.hist].sid)
                seen[kd.hist] = kd
            kids = sorted(seen.values(), key=lambda n: -n.score)
            done = [k for k in kids if k.done is not None]
            if done:
                for k in done:
                    self.e.mfree(k.sid)
                    k.sid = None
                pool.extend(done)
                kids = [k for k in kids if k.done is None]
                if first_done_step is None:
                    first_done_step = step
            if pool and (step - first_done_step >= self.post_steps or not kids):
                pool.sort(key=lambda n: (n.done, -n.st.get("hp", 0), -n.st.get("ninpo", 0)))
                best_done = pool[0]
                for k in kids:
                    self.e.mfree(k.sid)
                for g in gens:
                    for nd in g:
                        if nd.sid is not None and nd is not self.root:
                            self.e.mfree(nd.sid)
                            nd.sid = None
                self.width = base_width
                self.log(f"[{C.NAMES[self.stage]}] DONE {best_done.done} (ref {self.tas_load_next}, "
                         f"{best_done.done - self.tas_load_next:+d}) hp {best_done.st.get('hp')} ninpo "
                         f"{best_done.st.get('ninpo')} item {best_done.st.get('item')} evals {self.evals} "
                         f"{time.time() - t0:.0f}s; pool {sorted(n.done for n in pool)[:8]}")
                return best_done
            nb = self.select(kids)
            keep = set(id(k) for k in nb)
            for k in kids:
                if id(k) not in keep:
                    self.e.mfree(k.sid)
            if not nb:
                # every child died: back up and search wider
                f_now = beam[0].f
                backtracks = backtracks + 1 if abs(f_now - last_bt_frame) < 120 else 1
                last_bt_frame = f_now
                back = min(len(gens) - 1, 2 * backtracks + 1)
                if backtracks > 5 or back < 1:
                    self.log(f"[{C.NAMES[self.stage]}] beam empty at step {step} (f {f_now}); no more backtracking")
                    return None
                for _ in range(back):
                    for nd in gens.pop():
                        if nd.sid is not None:
                            self.e.mfree(nd.sid)
                            nd.sid = None
                beam = gens[-1]
                step -= back
                boost_until = step + back + 4
                self.log(f"[{C.NAMES[self.stage]}] all children died at f {f_now}: backtrack {back} generations "
                         f"(#{backtracks}), width x2 until step {boost_until}")
                continue
            beam = nb
            push_gen(beam)
            b = beam[0]
            hist_best.append(b.score - b.f)
            if self.explore_budget and len(hist_best) > self.stuck_steps and                     hist_best[-1] < hist_best[-self.stuck_steps - 1] - 0.5 * self.stuck_steps * self.chunk:
                # no progress (score relative to time) for stuck_steps full steps: explore around the obstacle
                target = max(n.score for n in beam) + (self.boss_w if self.boss else 24)
                self.log(f"[{C.NAMES[self.stage]}] stuck at f {b.f} (score {b.score:.1f}): exploring")
                fails = getattr(self, "_fails", 0)
                seeds = list(beam)
                if fails and self.checkpoints:
                    # repeated failure here: also start from older checkpoints (further back each time)
                    j = min(len(self.checkpoints), 2 * fails)
                    seeds += self.checkpoints[-j:]
                    self.log(f"[{C.NAMES[self.stage]}] explore seeds: + {j} checkpoints back to f {self.checkpoints[-j].f}")
                res = self.explore(seeds, self.explore_budget, target)
                self._fails = 0 if res else fails + 1
                hist_best.clear()
                if res:
                    nd = res[0]
                    if nd.done is not None:
                        pool.append(nd)
                        first_done_step = step - self.post_steps
                        continue
                    beam = [nd]
                    push_gen(beam)
                    b = nd
            if step % 10 == 0:
                if self.dump:
                    C.save_rows(self.dump, b.rows, f"best node at step {step}, start frame {self.f0}")
                s = b.st
                self.log(f"[{C.NAMES[self.stage]}] step {step} f {b.f} k {b.k} (lag {b.f - b.k:+d}) score {b.score:.1f} "
                         f"room {s['room']} ax {C.abs_x(s)} y {s['y']} hp {s['hp']} np {s['ninpo']} it {s['item']} "
                         f"evals {self.evals} {time.time() - t0:.0f}s")
            if b.f - self.f0 > self.max_frames or (deadline and time.time() > deadline):
                if pool:
                    pool.sort(key=lambda n: (n.done, -n.st.get("hp", 0), -n.st.get("ninpo", 0)))
                    self.log(f"[{C.NAMES[self.stage]}] time limit: returning the best finished node {pool[0].done}")
                    return pool[0]
                self.log(f"[{C.NAMES[self.stage]}] gave up at step {step}")
                return None
        return None
