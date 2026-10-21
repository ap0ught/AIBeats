"""One-off patch of contra/stages/s1_engine.py for rule v2 (purposeful fire, press budget). utf-8, temp file then
rename; the previous version is s1_engine.py.backup_v2."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s1_engine.py"
s = p.read_text(encoding="utf-8")


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:60], s.count(a))
    s = s.replace(a, b)


rep('''pit_ahead   early pit detection from the background collision map
"""''', '''pit_ahead   early pit detection from the background collision map

Rule v2 (2026-10-12; the version before it is s1_engine.py.backup_v2):
  * the press budget lives in s1_common.Pad: a press the budget refuses is missing from the row that is played, so
    every search here sees it as "cannot fire now";
  * the run policies no longer mash. New edit kind for the repair search: 'fire' (rows on which the policy fires
    at the fastest legal cadence whatever it sees - the old behaviour, locally) next to 'nofire'; among edits that
    reach the goal on the same row the one with the fewest B presses wins;
  * Repair(engage=...): "let it pass". When the policy is about to open fire on an enemy for the first time, the
    main run looks ahead with save states - once without ever firing at it, once firing - and fires only if not
    firing gets Bill killed or costs frames. The verdicts are kept in route.opts['dec'].
"""''')
rep('''    over    {row index: [edit, ...]}: per-frame edits found by the repair search in THIS run
            edit = ('add', button) | ('set', buttons) | ('aim', a) | ('nofire',) | ('nojump',)
    opts    free-form options the stage's policy reads (copied with the route)
    """''', '''    over    {row index: [edit, ...]}: per-frame edits found by the repair search in THIS run
            edit = ('add', button) | ('set', buttons) | ('aim', a) | ('nofire',) | ('nojump',) | ('fire',)
            ('fire',) and ('aim', a) = fire on this row at the fastest legal cadence, target or not
    opts    free-form options the stage's policy reads (copied with the route; the values are shared)
            'dec' = [(enemy slot, enemy type, first row, last row, 'pass' | 'shoot')]: the look-ahead verdicts
    """''')
rep('''            elif kind == "nofire":
                self.add_over(i, ("nofire",))
''', '''            elif kind == "nofire":
                self.add_over(i, ("nofire",))
            elif kind == "fire":
                self.add_over(i, ("fire",))
''')
rep('''    def fire_at(self, prog):
        for lo, hi in self.nofire:
            if lo <= prog < hi:
                return False
        return True
''', '''    def fire_at(self, prog):
        for lo, hi in self.nofire:
            if lo <= prog < hi:
                return False
        return True

    def verdict(self, row, slot, etype):
        """'pass' / 'shoot' if a look-ahead verdict covers this enemy slot on this (absolute) row, else None."""
        for d in reversed(self.opts.get("dec", ())):
            if d[0] == slot and d[1] == etype and d[2] <= row <= d[3]:
                return d[4]
        return None
''')
rep('''    def __init__(self, farm: Farm, policy, fail, ahead=110, tag="rep", verbose=True, plan=None, mark=None,
                 local=None):
        self.farm, self.policy, self.fail = farm, policy, fail
''', '''    def __init__(self, farm: Farm, policy, fail, ahead=110, tag="rep", verbose=True, plan=None, mark=None,
                 local=None, engage=None, look=170, fail_look=None):
        self.farm, self.policy, self.fail = farm, policy, fail
        self.engage = engage        # engage(g, route) -> (enemy slot, enemy type) the policy is about to open fire on, or None
        self.look = look            # rows of look-ahead for a "let it pass" verdict
        self.fail_look = fail_look or fail
        self.verdicts = {"pass": 0, "shoot": 0}
        self.look_rows = 0
''')
rep('''        g.load_file(state, pad)
        base = g.r.prog
        why, reached, k = None, False, 0
''', '''        g.load_file(state, pad)
        base = g.r.prog
        t_load = g.pad.t
        why, reached, k = None, False, 0
''')
rep('''        return {"ok": reached, "why": why or ("" if reached else "slow"), "frames": k, "prog": g.r.prog - base,
                "aprog": g.r.prog}
''', '''        return {"ok": reached, "why": why or ("" if reached else "slow"), "frames": k, "prog": g.r.prog - base,
                "aprog": g.r.prog, "presses": sum(1 for x in g.pad.starts["B"] if x >= t_load)}

    # ---- "let it pass": look ahead on the main game before the first shot at an enemy
    def _look(self, g: Game, route: Route, n, slot, etype):
        """Play n rows of the policy from g's state. Returns (survived, world X reached, rows until the enemy in
        `slot` was gone)."""
        gone = None
        route.opts["_look"] = True
        try:
            for k in range(n):
                g.step(self.policy(g, route))
                self.look_rows += 1
                if self.fail_look(g):
                    return False, g.r.prog, gone if gone is not None else k + 1
                e = g.r.enemy(slot)
                if gone is None and (e is None or e[1] != etype):
                    gone = k + 1
                if self.done is not None and self.done(g):
                    break
        finally:
            route.opts.pop("_look", None)
        return True, g.r.prog, gone if gone is not None else n

    def _decide(self, g: Game, route: Route):
        i = len(g.rows)
        if i < route.opts.get("decide_from", 0) or i in route.over:
            return
        eng = self.engage(g, route)
        if eng is None:
            return
        slot, etype = eng
        dec = route.opts.setdefault("dec", [])
        tok = g.snap()
        dec.append((slot, etype, i, i + self.look, "pass"))
        ok_a, prog_a, gone_a = self._look(g, route, self.look, slot, etype)
        g.restore(tok)
        verdict = "shoot"
        gone = self.look
        if ok_a:
            dec[-1] = (slot, etype, i, i + self.look, "shoot")
            ok_b, prog_b, gone = self._look(g, route, self.look, slot, etype)
            g.restore(tok)
            if not ok_b or prog_a >= prog_b:
                verdict, gone = "pass", gone_a
        # the verdict holds while this enemy is in its slot (as seen in the look-ahead that was chosen)
        dec[-1] = (slot, etype, i, i + max(8, gone), verdict)
        self.verdicts[verdict] += 1
        g.free(tok)
        if os.environ.get("S1_REPAIR_DEBUG"):
            log(f"      verdict row {i}: enemy slot {slot} type ${etype:02x} -> {verdict} (until row {i + max(8, gone)})")
''')
rep('''        for n in (10, 25, 60):
            for t in range(D - 6, t0, -st):
                if t - n >= t0:
                    c0.append(("nofire", t - n, n, None))
''', '''        for n in (10, 25, 60):
            for t in range(D - 6, t0, -st):
                if t - n >= t0:
                    c0.append(("nofire", t - n, n, None))
        for n in (10, 25, 60):
            for t in range(D - 6, t0, -st):
                if t - n >= t0:
                    c0.append(("fire", t - n, n, None))
''')
rep('''        oks = [(x["frames"], n, c) for n, (c, x) in enumerate(zip(cands, res)) if x["ok"]]
''', '''        # the soonest arrival wins; among equals the one that pressed B least, then the first in the list
        oks = [(x["frames"], x.get("presses", 0), n, c) for n, (c, x) in enumerate(zip(cands, res)) if x["ok"]]
''')
rep('''            oks.sort()
            return oks[0][2], oks[0][0] + i0, len(oks), None
''', '''            oks.sort(key=lambda t: t[:3])
            return oks[0][3], oks[0][0] + i0, len(oks), None
''')
rep('''        tok, i0, ed, arrive = fix
        route.apply_edit(ed)
        self.repairs.append((D, why, ed, arrive))
''', '''        tok, i0, ed, arrive = fix
        route.apply_edit(ed)
        self.repairs.append((D, why, ed, arrive))
        # the trial that chose this edit made no new look-ahead verdicts: neither does the main run until it is
        # past the row the trial reached, so that it replays the trial exactly
        route.opts["decide_from"] = max(route.opts.get("decide_from", 0), arrive if arrive is not None else D)
''')
rep('''                arrive = len(g.rows)
                log(f"   local search @{D} ({why}) from row {i0}: reaches X {ptarget} on row {arrive}, {time.time() - t_b:.0f} s"
''', '''                arrive = len(g.rows)
                route.opts["decide_from"] = max(route.opts.get("decide_from", 0), arrive)
                log(f"   local search @{D} ({why}) from row {i0}: reaches X {ptarget} on row {arrive}, {time.time() - t_b:.0f} s"
''')
rep('''                if name and name not in self.marks:
                    self.marks[name] = (len(g.rows), g.snap())
            g.step(self.policy(g, route))
''', '''                if name and name not in self.marks:
                    self.marks[name] = (len(g.rows), g.snap())
            if self.engage is not None:
                self._decide(g, route)
            g.step(self.policy(g, route))
''')
rep('''def local_beam(policy, fail, width=6, step=6, look_steps=4, tag="local", max_seconds=240):
    """A fallback for Repair: beam search over `step`-frame choices on top of the run policy - R (as the policy
    says), J (jump now), NJ (skip a planned jump), P (duck and fire), S (stand and fire) - for the fewest frames
    to the goal."""

    def run(g: Game, route: Route, until):
        def rows(g, a, k):
            if a == "P":
                return fire(g.pad, {"Down"})
            if a == "S":
                return fire(g.pad, set())
''', '''def local_beam(policy, fail, width=6, step=6, look_steps=4, tag="local", max_seconds=240, shoot=None):
    """A fallback for Repair: beam search over `step`-frame choices on top of the run policy - R (as the policy
    says), J (jump now), NJ (skip a planned jump), P (duck and fire), S (stand and fire) - for the fewest frames
    to the goal. shoot(g, want) adds B to `want` for P and S (default: the fastest legal cadence; the rule v2
    policies pass their own version, which keeps the press plan's headroom)."""
    shoot = shoot or (lambda g, w: fire(g.pad, w))

    def run(g: Game, route: Route, until):
        def rows(g, a, k):
            if a == "P":
                return shoot(g, {"Down"})
            if a == "S":
                return shoot(g, set())
''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("s1_engine.py patched")
