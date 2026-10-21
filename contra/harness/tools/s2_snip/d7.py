# reproduce stage 2 room 5 from the pause-5 start condition and show what the driver runs into
import json
import contra.stages.base_room as br
rep = json.load(open("logs/s2/p5_report.json"))
rows = [tuple(r) for r in json.load(open("logs/s2/p5_rows.json"))]
load = rep["rooms"][4]["load"]
S = bc.Sess(e, fields=bc.make_fields())
S.load("ref_s2")
for r in rows[:load]:
    S.step(r)
print("at room", S.s["screen"] + 1, "row", len(S.rows), "fc", S.s["frame_fc"])
e.save("s2/p5_room5")
G["p5S"] = S
G["p5snap"] = S.snapshot()
rs = br.RoomSolver(S, beam=12000, verbose=True, max_replans=G.get("MAXRP", 10))
R = rs.solve(G["p5snap"])
print(R)
