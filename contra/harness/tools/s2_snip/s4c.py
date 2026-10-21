import importlib, contra.stages.base_plan as bp, contra.stages.base_room as br
S = G["S4"]; S.e.set_fields(bc.make_fields())
START = G.get("START4", 1)
S.restore(G[f"s4_snap_room{START}"])
S.s = bc.State.parse(S.e.cmd("state"))
rs = br.RoomSolver(S, beam=G.get("BEAM", 12000), ntop=4)
for room in range(START, 9):
    snap0 = S.snapshot()
    G[f"s4_snap_room{room}"] = snap0
    if S.s["loc"] & 0x80:
        print("boss room reached"); break
    R = rs.solve(snap0)
    print(room, R, "frames", len(S.rows) - len(snap0[1]))
    if R.plan: print(R.plan)
    G[f"s4_R{room}"] = R
    if not R.ok: break
G["s4_snap_after"] = S.snapshot()
print("rows", len(S.rows), {k: S.s[k] for k in ("frame","screen","x","y","cores","loc")})
