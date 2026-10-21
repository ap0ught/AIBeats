import importlib, time, json
import contra.stages.s2 as s2
S = G["S"]; S.e.set_fields(bc.make_fields())
S.restore(G["snap_after"]); S.s = S.e.state() if False else bc.State.parse(S.e.cmd("state"))
n0 = len(S.rows)
b = s2.solve_boss(S, width=G.get("BW", 12))
print("boss", b, {k: S.s[k] for k in ("x", "y", "frame", "bossdef", "plates")})
if b["ok"]:
    G["snap_bossdead"] = S.snapshot()
    x = s2.solve_exit(S)
    print("exit", x, {k: S.s[k] for k in ("frame", "level", "lroutine", "weapon", "lives", "x", "y")})
    print("stage frames", len(S.rows), "end frame", S.s["frame"])
    json.dump(S.rows, open("logs/s2/v0_rows.json", "w"))
    G["snap_s3"] = S.snapshot()
