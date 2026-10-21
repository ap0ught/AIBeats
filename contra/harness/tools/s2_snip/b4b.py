# stage 4 boss + exit from the saved boss-room snapshot
import json
import contra.stages.base_boss as bb
import contra.stages.s4 as s4
S = G["S4"]
S.e.set_fields(bc.make_fields())
S.restore(G["s4_snap_after"])
S.s = bc.State.parse(S.e.cmd("state"))
json.dump(S.rows, open("logs/s4/v0_rows_to_boss.json", "w"))
S.e.save("s4/v0_boss")
print("boss room", {k: S.s[k] for k in ("frame", "x", "y", "loc", "cores")}, bc.fmt_enemies(S.s)[:300])
b = bb.solve_boss(S, width=G.get("BW", 12), **s4.BOSS)
print("boss", b, {k: S.s[k] for k in ("x", "y", "frame", "bossdef", "plates", "cores")})
if b["ok"]:
    G["s4_snap_bossdead"] = S.snapshot()
    x = bb.solve_exit(S)
    print("exit", x, {k: S.s[k] for k in ("frame", "level", "lroutine", "weapon", "lives")})
    print("stage frames", len(S.rows))
    json.dump(S.rows, open("logs/s4/v0_rows.json", "w"))
