import os

ROOT = ""


def patch(path, reps):
    p = ROOT + path
    s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)


patch("contra/stages/s2.py", [
    ('''    b = (boss["fn"](S, width=boss_width, hold=boss_hold) if "fn" in boss
         else bb.solve_boss(S, width=boss_width, hold=boss_hold, **boss))
''', '''    if "fn" in boss:
        b = boss["fn"](S, width=boss_width, hold=boss_hold)
    else:
        # the beam search is greedy and its result moves by tens of frames with its width: run a few, keep the best
        snap_b = S.snapshot()
        best_b = None
        tried = []
        for w, h in ((20, 4), (boss_width, boss_hold), (16, 3)):
            S.restore(snap_b)
            bi = bb.solve_boss(S, width=w, hold=h, **boss)
            tried.append((w, h, bi.get("frames"), bi.get("ok")))
            if bi["ok"] and (best_b is None or bi["frames"] < best_b[0]["frames"]):
                best_b = (bi, S.snapshot())
        if best_b:
            S.restore(best_b[1])
            b = best_b[0]
        else:
            b = bi
        b["variants"] = tried
'''),
])
print("patched")
