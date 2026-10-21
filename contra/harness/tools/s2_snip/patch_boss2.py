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


patch("contra/stages/base_boss.py", [
    ('''    targets: [(key, x, y, code, capacity, vx)] (vx = target's X speed, bouncing between 80 and 176) -> {key: n}."""''',
     '''    targets: [(key, x, y, code, capacity, vx, t_open)] (vx = target's X speed, bouncing between 80 and 176;
    t_open = frames until it can be hit, bullets pass through before that) -> {key: n}."""'''),
    ("    tg = [[key, float(ex), ey, code, cap, vx] for key, ex, ey, code, cap, vx in targets]\n    for _ in range(frames):\n        for t in tg:\n            if cnt[t[0]] >= t[4]:\n                continue",
     "    tg = [[key, float(ex), ey, code, cap, vx, op] for key, ex, ey, code, cap, vx, op in targets]\n    for f in range(frames):\n        for t in tg:\n            if cnt[t[0]] >= t[4] or f < t[6]:\n                continue"),
    ("            inc = incoming(s, [(i, x, y, 2, hp, 0) for i, x, y, hp in ps])",
     "            inc = incoming(s, [(i, x, y, 2, hp, 0, 0) for i, x, y, hp in ps])"),
    ('''        tg, wait = [], 0
        for i in fs:
            if s[f"es{i}"] & 0x80:
                wait += hp_full if s[f"{hp_field}{i}"] in (0, hp_full) else s[f"{hp_field}{i}"]
            else:
                vx = (s[f"evx{i}"] - (256 if s[f"evx{i}"] >= 128 else 0) + s[f"efx{i}"] / 256.0) if moving else 0
                tg.append((i, s[f"ex{i}"], s[f"ey{i}"], s[f"ec{i}"] & 15, s[f"{hp_field}{i}"], vx))
        if not tg:                               # nothing vulnerable: wait under the middle, on the ground
            return (1, wait, wait, abs(s["x"] - 128) + abs(s["y"] - ground_y))
        inc = incoming(s, tg, frames=30)''',
     '''        tg, wait = [], 0
        for i in fs:
            hp = s[f"{hp_field}{i}"] or hp_full
            if s[f"es{i}"] & 0x80:
                if s[f"er{i}"] == 2 and 0 < s[f"ed{i}"] <= 40:
                    # first appearance: becomes vulnerable when its delay runs out; bullets may be sent ahead
                    tg.append((i, s[f"ex{i}"], s[f"ey{i}"], 2, hp, 0, s[f"ed{i}"]))
                else:
                    wait += hp
            else:
                vx = (s[f"evx{i}"] - (256 if s[f"evx{i}"] >= 128 else 0) + s[f"efx{i}"] / 256.0) if moving else 0
                tg.append((i, s[f"ex{i}"], s[f"ey{i}"], s[f"ec{i}"] & 15, hp, vx, 0))
        if not tg:                               # nothing vulnerable soon: wait below a target
            xs = [s[f"ex{i}"] for i in fs]
            return (1, wait, wait, min(abs(s["x"] - x) for x in xs) + abs(s["y"] - ground_y))
        inc = incoming(s, tg, frames=40)'''),
])
print("patched")
