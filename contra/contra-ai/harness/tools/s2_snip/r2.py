import importlib, contra.stages.base_plan as bp, contra.stages.base_room as br
importlib.reload(bp); importlib.reload(br)
S = G["S"]; S.e.set_fields(bc.make_fields())
START = G.get("START", 2)
S.restore(G["snap_r2"] if START == 2 else G[f"snap_room{START}"])
rs = br.RoomSolver(S, beam=12000, ntop=4)
for room in range(START, 6):
    snap0 = S.snapshot()
    G[f"snap_room{room}"] = snap0
    if S.s["loc"] & 0x80:
        print("boss room reached"); break
    R = rs.solve(snap0)
    print(room, R)
    if R.plan: print(R.plan)
    G[f"R{room}"] = R
    if not R.ok: break
G["snap_after"] = S.snapshot()
print("rows", len(S.rows), {k: S.s[k] for k in ("frame","screen","x","y","cores","loc")})
