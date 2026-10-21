"""Second-pass patch 18: the door grid tries the hover option too."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''BOSS_GRID = [(j1, ph, j2, band, ab) for j1 in (None, 40, 43, 45, 47, 50, 54, 58)
             for ph in range(5) for j2 in (None,) for band in ((112, 144),) for ab in ("Down",)]''',
    '''BOSS_GRID = [(j1, ph, j2, band, ab, hv) for j1 in (None, 40, 43, 45, 47, 50, 54, 58)
             for ph in range(5) for j2 in (None,) for band in ((112, 144),) for ab in ("Down",)
             for hv in ((None, 166) if j1 is None else (None,))]''')
rep('''        j1, ph, j2, band, ab = par
        try:
            n = boss_try(c, j1, ph, j2, band, ab)
        except Fail:''', '''        j1, ph, j2, band, ab, hv = par
        try:
            n = boss_try(c, j1, ph, j2, band, ab, hover=hv)
        except Fail:''')
rep('''            j1b, phb, j2b, bandb, abb = best[1]
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
        boss_try(c, j1, ph, j2, band, ab)''',
    '''            j1b, phb, j2b, bandb, abb, hvb = best[1]
            near = [j1b] if j1b is None else [j1b - 1, j1b + 1, j1b - 3, j1b + 3]
            for j1 in near:
                for ph in range(5):
                    run((j1, ph, j2b, bandb, abb, hvb))
            j1b, phb, j2b, bandb, abb, hvb = best[1]
            for hv in (None, 160, 164, 168, 172):
                for ph in range(5):
                    run((j1b, ph, j2b, bandb, abb, hv))
            j1b, phb, j2b, bandb, abb, hvb = best[1]
            for j2 in (None, 150, 160, 168, 176):
                for band in ((112, 144), (106, 150), (116, 140)):
                    for ab in ("Down", ""):
                        run((j1b, phb, j2, band, ab, hvb))
        c.restore(base)
        j1, ph, j2, band, ab, hv = best[1]
        boss_try(c, j1, ph, j2, band, ab, hover=hv)''')
rep('''    r.log(f"[{r.name}] door: {best[0]} rows: first jump at scroll frame {j1}, fire phase {ph}, second jump {j2}, "
          f"band {band}, above {ab!r} ({tried} attempts)")''',
    '''    r.log(f"[{r.name}] door: {best[0]} rows: first jump at scroll frame {j1}, fire phase {ph}, second jump {j2}, "
          f"band {band}, above {ab!r}, hover {hv} ({tried} attempts)")''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
