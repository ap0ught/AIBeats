import contra.stages.base_plan as bp, contra.stages.base_room as br
S = G["S4"]
room = G.get("DROOM", 2)
tr, dead = br.record_room(S, G[f"s4_snap_room{room}"], 440)
ents = bp.entities_from_trace(tr)
print("dead", dead, "land", next((T for T in range(1, len(tr)) if tr[T]["jump"] == 0 and tr[T]["y"] >= 160), None), "x", tr[60]["x"])
for en in ents: print(en, "attr", en.attr)
G["dbg_ents"] = ents; G["dbg_tr"] = tr
