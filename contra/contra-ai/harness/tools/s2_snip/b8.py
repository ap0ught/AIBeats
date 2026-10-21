# stage 4 boss with the scripted helmet attack, from the saved boss-room disk state
import json
import contra.stages.base_boss as bb
import contra.stages.base_boss4 as b4

rows0 = [tuple(r) for r in json.load(open("logs/s4/v0_rows_to_boss.json"))]
S = bc.Sess(e, hist=rows0[-40:], fields=bc.make_fields())
S.load("s4/v0_boss")
info = b4.solve_boss(S, width=G.get("BW", 12), hold=4)
print("boss", info)
print({k: S.s[k] for k in ("x", "y", "frame", "bossdef", "plates", "cores")})
if info["ok"]:
    x = bb.solve_exit(S)
    print("exit", x, {k: S.s[k] for k in ("frame", "level", "lroutine", "weapon", "lives")})
    full = rows0 + list(S.rows)
    json.dump(full, open("logs/s4/v1_rows.json", "w"))
    print("stage frames", len(full))
