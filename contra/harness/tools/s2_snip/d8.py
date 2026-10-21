import contra.stages.base_room as br
S = G["p5S"]
S.e.set_fields(bc.make_fields())
rs = br.RoomSolver(S, beam=12000, verbose=True, max_replans=G.get("MAXRP", 12))
R = rs.solve(G["p5snap"])
print(R)
