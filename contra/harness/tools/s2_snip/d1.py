import importlib, contra.stages.base_plan as bp, contra.stages.base_room as br
importlib.reload(bp); importlib.reload(br)
ents = G["r1_ents"]
plans = bp.plan_room(ents, 33, 112, 112, t_max=400, beam=12000, ntop=3)
p = plans[0]
print(p)
prev=None
for i in range(1, len(p.presses)+1):
    path = br.choose_path(p.presses[:i], 112, 0, 32)
    (T,k,mR,mL,hk) = p.presses[i-1]
    a,b = bp.mask_list(mR), bp.mask_list(mL)
    print(i, "T",T,"k",k,hk,"R",(a[0],a[-1]) if a else None,"L",(b[0],b[-1]) if b else None, "path ok" if path else "NOPATH", path[-1] if path else "")
    if not path: break
