"""Room 3 of stage 4 only, entered from the tail of the q0 run's room 2 (the old driver's rows are replayed up to
its last press, so the re-walk can be tested without solving room 2 again)."""
import json, time
from contra.stages.base_common import Sess, make_fields
from contra.stages import base_room3 as br3

rep = json.load(open("logs/s4/q0_report.json"))
rows = [tuple(r) for r in json.load(open("logs/s4/q0_rows.json"))]
r2, r3 = rep["rooms"][1], rep["rooms"][2]
em = E[0]
S = Sess(em, fields=make_fields())
S.load("s4/q0/room2")
last_press = r2["plan"][-1][0]
for r in rows[r2["load"]:r2["load"] + last_press + 2]:
    S.step(S.pad.fix(r))
tail = S.snapshot()
T_tail = last_press + 2
rs = br3.RoomSolver3(S, verbose=True)
Tc, Tn, d = rs._walk(T_tail)
print("old walk: cleared", Tc, "next", Tn, "death", d, "x", S.s["x"])
prev = dict(snap=tail, T=T_tail, x=tail[3]["x"], T_next=Tn)
snap0 = S.snapshot()
t0 = time.time()
R = rs.solve(snap0, prev=prev)
print(f"ROOM 3: ok {R.ok} {R.reason} last hit T{R.T_last_hit} next {R.T_next} lag {R.lag} replans {R.replans} secs {time.time() - t0:.0f}")
print("   ", R.plan)
