# record room 1 passively, build entities, run the planner
import time
import importlib
import contra.stages.base_plan as bp
importlib.reload(bp)
e.set_fields(bc.make_fields())
e.mload(G["s2_0"])
e.trace(True)
e.run(bc.rows_from_spec(430, [(40, 430, "Down")]))
tr = e.last_trace
e.trace(False)
G["r1_trace"] = tr
ents = bp.entities_from_trace(tr)
for en in ents:
    print(en)
G["r1_ents"] = ents
t = time.time()
plans = bp.plan_room(ents, 34, 96, 144, t_max=400, beam=20000, ntop=5, verbose=True)
print("time", round(time.time() - t, 1))
for p in plans:
    print(p)
    for (T, k, mR, mL, hk) in p.presses:
        a, b = bp.mask_list(mR), bp.mask_list(mL)
        print("   T", T, "k", k, "hits", hk, "pxR", (a[0], a[-1]) if a else None, "pxL", (b[0], b[-1]) if b else None)
    break
G["r1_plans"] = plans
