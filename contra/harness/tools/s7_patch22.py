"""Second-pass patch 22: the runner (with its remedies) carries Bill 16 frames INTO the reveal scroll before the
door procedure takes over (a gunner's bullet killed every scripted fight 15 rows after the old hand-over point);
the scroll frame is read from the auto-scroll counter; an emergency grid with earlier jumps."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''    while not c.f["bossdef"]:
        f = c.f
        if f["stop"] == 0xFF and s < 0:
            s = 0
        g = grounded(f)
        want = {"Right"}
        if s >= 0:''', '''    while not c.f["bossdef"]:
        f = c.f
        if f["stop"] == 0xFF:
            if f["auto"] > 0:
                s = 95 - f["auto"]          # scroll frame, also when the script starts inside the scroll
            elif s < 0:
                s = 96
        g = grounded(f)
        want = {"Right"}
        if s >= 0:''')
rep('''            s += 1
        fr = _fr(c, want, log)
        t += 1
        if t > limit:
            raise Fail("door not dead in time")''', '''            if f["auto"] == 0:
                s += 1
        fr = _fr(c, want, log)
        t += 1
        if t > limit:
            raise Fail("door not dead in time")''')
rep('''        for par in BOSS_GRID:
            run(par)
        if best is None:
            raise Stuck(f"door: no scripted fight worked: {why}")''', '''        for par in BOSS_GRID:
            run(par)
        if best is None:
            # emergency: earlier first jumps (something on the ground kills every line of the normal grid)
            for j1 in (18, 22, 26, 30, 34, 37):
                for ph in range(5):
                    for j2 in (None, 150):
                        run((j1, ph, j2, (112, 144), "Down", None))
        if best is None:
            raise Stuck(f"door: no scripted fight worked: {why}")''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
rep('''        Until(lambda r: r.c.f.cam >= 3488 - 24, ("Right",), "boss approach"),
        Mark("boss_beam"),''', '''        # second pass: the door procedure takes over 16 frames into the reveal scroll (camera 3504); the first
        # pass's beam search started 24 px before the scroll
        Until((lambda r: r.c.f.cam >= 3488 - 24) if p.get("boss_beam") else (lambda r: r.c.f.cam >= 3504),
              ("Right",), "boss approach"),
        Mark("boss_beam"),''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
