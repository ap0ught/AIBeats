import importlib, time, contra.stages.base_boss as bb
importlib.reload(bb)
S = G["S"]
S.restore(G["snap_after"])
# hop: nothing until landed
n = 0
while not (S.s["jump"] == 0 and S.s["y"] > 190) and n < 120:
    S.step(()); n += 1
print("landed after", n, {k: S.s[k] for k in ("x", "y", "frame")})
snapL = S.snapshot(); G["snapL"] = snapL
def plates(s):
    return [(i, s[f"ex{i}"], s[f"ey{i}"], 10 if s[f"eh{i}"] >= 0xF0 else s[f"eh{i}"]) for i in range(16) if s[f"er{i}"] and s[f"et{i}"] == 0x0A and s[f"eh{i}"] > 0]
def eye(s):
    for i in range(16):
        if s[f"er{i}"] and s[f"et{i}"] == 0x10:
            return i
    return None
def score(s):
    ps = plates(s)
    if s["plates"] < 4 and ps:
        tot = sum(p[3] for p in ps)
        dist = min(abs(s["x"] - p[1]) for p in ps)
        return (0, -s["plates"], tot, dist)
    i = eye(s)
    if i is None:
        return (1, 0, 0, 0)
    return (1, s[f"e1{i}"] if (s[f"es{i}"] & 0x80) == 0 else 16, abs(s["x"] - s[f"ex{i}"]) + (40 if s["jump"] else 0), 0)
def done(s):
    return s["bossdef"] != 0
t = time.time()
goal, layers = bb.beam(S, snapL, score, done, max_layers=100, width=10, hold=4, verbose=False)
print("beam", layers, "time", round(time.time() - t))
if goal:
    S.restore(goal); G["snap_bossdead"] = goal
    print("boss dead at step", len(S.rows) - len(G["rows_to_boss"]), {k: S.s[k] for k in ("x", "y", "frame", "bossdef", "plates")})
