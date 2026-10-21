"""Second one-off patch for rule v2: planned pre-fire. Repair records the row on which every hostile target first
appears in the main run (sight=...); after a death its free edits include short and long stretches of cadence
fire that START 30-46 rows before such a row - the time a volley needs to reach the screen edge - so that the
pellets are there when the enemy appears. (Measured in stage 5: a turret man fires 39 frames after he appears and
has 10 HP; fire that only starts when he is seen kills him too late, the old permanent mash killed him by luck of
its phase, and only volleys fired 40-41 rows before he appears do it reliably.)"""
from pathlib import Path

root = Path(__file__).resolve().parent.parent / "contra" / "stages"


def patch(name, reps):
    p = root / name
    s = p.read_text(encoding="utf-8")
    for a, b in reps:
        assert s.count(a) == 1, (name, a[:70], s.count(a))
        s = s.replace(a, b)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(s, encoding="utf-8")
    tmp.replace(p)
    print(name, "patched")


patch("s1_engine.py", [
    ('''                 local=None, engage=None, look=170, fail_look=None):
        self.farm, self.policy, self.fail = farm, policy, fail
''', '''                 local=None, engage=None, look=170, fail_look=None, sight=None):
        self.farm, self.policy, self.fail = farm, policy, fail
        self.sight = sight          # sight(g) -> [(enemy slot, enemy type)] of the hostile targets present
        self.sightings = []         # [(row of the main run on which a target first appeared, (slot, type))]
        self._seen = None
'''),
    ('''        for n in (10, 25, 60):
            for t in range(D - 6, t0, -st):
                if t - n >= t0:
                    c0.append(("fire", t - n, n, None))
''', '''        for n in (10, 25, 60):
            for t in range(D - 6, t0, -st):
                if t - n >= t0:
                    c0.append(("fire", t - n, n, None))
        # planned pre-fire: volleys timed to arrive when an enemy that appeared shortly before the failure appears
        for (srow, _key) in self.sightings:
            if D - 90 <= srow < D:
                for n in (7, 12, 45, 80):
                    for t in range(srow - 46, srow - 29, 2):
                        if t >= t0 and ("fire", t, n, None) not in c0:
                            c0.append(("fire", t, n, None))
'''),
    ('''        route.opts["decide_from"] = max(route.opts.get("decide_from", 0), arrive if arrive is not None else D)
''', '''        route.opts["decide_from"] = max(route.opts.get("decide_from", 0), arrive if arrive is not None else D)
        self.sightings = [x for x in self.sightings if x[0] <= i0]
        self._seen = None
'''),
    ('''                arrive = len(g.rows)
                route.opts["decide_from"] = max(route.opts.get("decide_from", 0), arrive)
''', '''                arrive = len(g.rows)
                route.opts["decide_from"] = max(route.opts.get("decide_from", 0), arrive)
                self.sightings = [x for x in self.sightings if x[0] <= i0]
                self._seen = None
'''),
    ('''            if self.engage is not None:
                self._decide(g, route)
            g.step(self.policy(g, route))
''', '''            if self.engage is not None:
                self._decide(g, route)
            g.step(self.policy(g, route))
            if self.sight is not None:
                cur = set(self.sight(g))
                if self._seen is not None:
                    for key in cur - self._seen:
                        self.sightings.append((len(g.rows), key))
                self._seen = cur
'''),
])
patch("s1.py", [
    ('''def shoot_planned(g: Game, w: set):
''', '''def sight(g: Game):
    """For s1_engine.Repair: the hostile targets present, as (slot, type)."""
    return [(t[0], t[1]) for t in _sort_enemies(g.r)[0]]


def shoot_planned(g: Game, w: set):
'''),
    ('''local=local_beam(policy, fail, tag=f"s1_{out}", shoot=shoot_planned), engage=engage)
''', '''local=local_beam(policy, fail, tag=f"s1_{out}", shoot=shoot_planned), engage=engage, sight=sight)
'''),
])
patch("s5.py", [
    ('''def shoot_planned(g: Game, w: set):
''', '''def sight(g: Game):
    """For s1_engine.Repair: the hostile targets present, as (slot, type)."""
    return [(e[0], e[1]) for e in g.r.enemies() if e[1] in TARGETS and not (e[6] & 0x80) and 0 < e[3] < 0xF0]


def shoot_planned(g: Game, w: set):
'''),
    ('''                  engage=engage, fail_look=fail_hard)
''', '''                  engage=engage, fail_look=fail_hard, sight=sight)
'''),
])
