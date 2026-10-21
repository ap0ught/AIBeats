"""Run the third-pass room driver over consecutive rooms from a saved room state.
G['T1'] = (state, n_rooms, emulator index) set by the caller's wrapper (or defaults below)."""
import importlib, sys, json, time
from contra.stages.base_common import Sess, make_fields
from contra.stages import base_room3 as br3

state, nrooms, ei = G.get("T1", ("s4/q0/room2", 2, 0))
em = E[ei]
S = Sess(em, fields=make_fields())
S.load(state)
snap0 = S.snapshot()
rs = br3.RoomSolver3(S, verbose=True)
prev = None
for k in range(nrooms):
    n0 = len(S.rows)
    t0 = time.time()
    R = rs.solve(snap0, prev=prev)
    print(f"ROOM +{k}: ok {R.ok} {R.reason} last hit T{R.T_last_hit} cleared {R.T_cleared} next {R.T_next} lag {R.lag} replans {R.replans} "
          f"rows {len(S.rows) - R.n_load if R.ok else None} secs {time.time() - t0:.0f}")
    if R.plan:
        print("   ", R.plan)
    if not R.ok:
        break
    prev = getattr(R, "tail", None)
    snap0 = S.snapshot()
print("total rows", len(S.rows))
