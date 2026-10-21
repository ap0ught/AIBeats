import importlib, contra.stages.base_plan as bp, contra.stages.base_room as br
importlib.reload(bp); importlib.reload(br)
S = bc.Sess(e)
S.load("ref_s2")
S.step(())
snap0 = S.snapshot()
rs = br.RoomSolver(S, beam=12000, ntop=4)
R = rs.solve(snap0)
print(R)
if R.plan: print(R.plan)
G["S"] = S; G["R1"] = R
if R.ok:
    G["snap_r2"] = S.snapshot()
    print("rows", len(S.rows), "state", {k: S.s[k] for k in ("frame","screen","x","y","cores","frame_fc")})
