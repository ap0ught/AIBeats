"""Second-pass patch 2: replace the scripted door fight in contra/stages/s7b.py (utf-8, temp file + rename)."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
a = s.index("def boss_try(")
new = '''def boss_try(c, j1, phase, j2=None, band=(112, 144), above="Down", up_s=60, limit=330, log=None):
    """Scripted door fight from a state shortly before the reveal scroll. Right is always held.
    j1      scroll frame of the first jump (None = never)
    j2      None = no further jump; a number = jump again when on the ground at screen x >= j2
    phase   a new B press on frames with t % 5 == phase (t counts from the first frame of the script)
    band    Y range in which an airborne shot is aimed forward (the core's height); higher up it is aimed
            `above` ("Down" = down-forward, "" = forward), lower it is aimed up-forward
    up_s    on the ground the shots are aimed up-forward from this scroll frame on
    Returns the number of rows until the door's HP is 0 (BOSS_DEFEATED set), or raises Fail."""
    n0 = len(c.rows)
    s = -1                       # frames since the scroll started
    t = 0
    jumps = 0
    while not c.f["bossdef"]:
        f = c.f
        if f["stop"] == 0xFF and s < 0:
            s = 0
        g = grounded(f)
        want = {"Right"}
        if s >= 0:
            if g and c.can("A"):
                if jumps == 0 and j1 is not None and s >= j1:
                    want.add("A")
                    jumps += 1
                elif jumps > 0 and j2 is not None and f["x"] >= j2:
                    want.add("A")
                    jumps += 1
            air = (not g) or ("A" in want) or ("A" in c.pr.held and c.pr.must_hold("A"))
            if (t % 5) == phase and c.can("B"):
                want.add("B")
            if air:
                y = f["y"]
                if y < band[0]:
                    if above:
                        want.add(above)
                elif y > band[1]:
                    want.add("Up")
            elif s >= up_s:
                want.add("Up")
            s += 1
        fr = _fr(c, want, log)
        t += 1
        if t > limit:
            raise Fail("door not dead in time")
    return len(c.rows) - n0


BOSS_GRID = [(j1, ph, j2, band, ab) for j1 in (None, 40, 44, 46, 48, 50, 52, 54, 56, 58, 60)
             for ph in range(5) for j2 in (None,) for band in ((112, 144),) for ab in ("Down",)]


def boss_proc2(r):
    """Runner Proc: the door fight by a parameter grid, then a refinement around the best."""
    c = r.c
    sod = c.stop_on_death
    c.stop_on_death = False
    base = c.snap()
    best = None
    tried = 0
    seen = set()

    def run(par):
        nonlocal best, tried
        if par in seen:
            return
        seen.add(par)
        c.restore(base)
        tried += 1
        j1, ph, j2, band, ab = par
        try:
            n = boss_try(c, j1, ph, j2, band, ab)
        except Fail:
            r.frames_simulated += len(c.rows) - base["n"]
            return
        r.frames_simulated += n
        if best is None or n < best[0]:
            best = (n, par)

    try:
        for par in BOSS_GRID:
            run(par)
        if best is None:
            raise Stuck("door: no scripted fight worked")
        for _ in range(2):
            j1b, phb, j2b, bandb, abb = best[1]
            near = [j1b] if j1b is None else [j1b - 1, j1b + 1, j1b - 3, j1b + 3]
            for j1 in near:
                for ph in range(5):
                    run((j1, ph, j2b, bandb, abb))
            j1b, phb, j2b, bandb, abb = best[1]
            for j2 in (None, 150, 160, 168, 176):
                for band in ((112, 144), (106, 150), (116, 140)):
                    for ab in ("Down", ""):
                        run((j1b, phb, j2, band, ab))
        c.restore(base)
        j1, ph, j2, band, ab = best[1]
        boss_try(c, j1, ph, j2, band, ab)
    finally:
        c.free(base)
        c.stop_on_death = sod
    r.user["boss"] = {"rows": best[0], "params": list(best[1]), "tried": tried}
    r.log(f"[{r.name}] door: {best[0]} rows: first jump at scroll frame {j1}, fire phase {ph}, second jump {j2}, "
          f"band {band}, above {ab!r} ({tried} attempts)")
    r.marks.append(("boss_killed", len(c.rows), c.f["fc"], c.f.wx, c.f["y"]))
'''
s = s[:a] + new
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
