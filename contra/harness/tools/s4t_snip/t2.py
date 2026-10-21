"""Debug: stage 4 room 3 with a given entry: plan (fixed entry), execute once, print the failure context."""
import time
from contra.stages.base_common import Sess, make_fields
from contra.stages import base_room3 as br3
from contra.stages import base_plan3 as bp

em = E[0]
S = Sess(em, fields=make_fields())
S.load(G.get("T2", "s4/q0/room3"))
snap0 = S.snapshot()
rs = br3.RoomSolver3(S, verbose=True)
A = rs.analyse(snap0, 440)
m = bp.mask_range(A["px"], A["px"])
entry = (0, m) if A["face"] else (m, 0)
hp_over = {eid: 23 for eid in A["plated"]}
t0 = time.time()
plans = bp.plan_room(A["ents"], A["T_land"] + 1, entry, A["air_y"], hp_over=hp_over, t_max=430, beam=12000, ntop=6,
                     plated=A["plated"], keep=2, t0=2)
print("plan", plans[0].finish, round(time.time() - t0), "s")
rows, pos = rs.build_rows(plans[0], A["T_land"], (A["px"], A["face"]))
print("positions", [(p[0], pos[i]) for i, p in enumerate(plans[0].presses)])
print("rows", " ".join(f"{T}:{'+'.join(r)}" for T, r in sorted(rows.items()) if r))
st, info = rs.execute(snap0, plans[0], A["ents"], A["T_land"], (A["px"], A["face"]))
print(st, {k: v for k, v in info.items() if k not in ("hits", "tail")})
