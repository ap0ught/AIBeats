import importlib, contra.stages.base_plan as bp, contra.stages.base_room as br
S = bc.Sess(e)
s = S.load("dbg/s4_pre")
print({k: s[k] for k in ("frame", "level", "lroutine", "weapon", "lives", "frame_fc")})
n = 0
while S.s["lroutine"] != 4 and n < 400:
    S.step(()); n += 1
print("L after", n, {k: S.s[k] for k in ("frame", "level", "lroutine", "weapon", "lives", "frame_fc")})
e.save("s4/dbg_L")
S.rows = []
S.step(())
G["S4"] = S
G["s4_snap_room1"] = S.snapshot()
tr, dead = br.record_room(S, G["s4_snap_room1"], 200)
ents = bp.entities_from_trace(tr)
for en in ents: print(en)
c = [en for en in ents if en.kind == "core"][0]
i = c.slot
last = None
for T, s in enumerate(tr):
    cur = (s[f"er{i}"], s[f"eh{i}"], s[f"es{i}"], s[f"ec{i}"])
    if cur != last: print(T, "core r,hp,st,code", cur, "jump", s["jump"], "y", s["y"], "x", s["x"])
    last = cur
