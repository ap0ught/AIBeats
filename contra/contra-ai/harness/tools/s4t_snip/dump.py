"""Record every room of a solved run passively (crouching, as base_room.record_room does) and save the traces as
plain dicts for offline planner work: logs/s4t/rooms_<stage>.pkl = {room: {"tr": [dict], "dead": T, "jump_y": [...]}}"""
import importlib, sys, json, pickle
sys.path.insert(0, "tools")
import s4t_lab as L
importlib.reload(L)
from contra.stages.base_common import Sess, make_fields
from contra.stages import base_room as br

for stage, pre, nrooms in ((4, "s4/q0", 8), (2, "s2/L0", 5)):
    out = {}
    for room in range(1, nrooms + 1):
        S = Sess(e, fields=make_fields())
        S.load(f"{pre}/room{room}")
        snap0 = S.snapshot()
        tr, dead = br.record_room(S, snap0, 600)
        T_land = next((T for T in range(1, len(tr)) if tr[T]["jump"] == 0 and tr[T]["y"] >= 160), 40)
        rs = br.RoomSolver(S, verbose=False)
        jy = rs.jump_table(snap0, T_land)
        out[room] = {"tr": [dict(s) for s in tr], "dead": dead, "jump_y": jy, "T_land": T_land}
        print(stage, room, "T_land", T_land, "px", tr[T_land]["x"], "dead", dead, "jump frames", len(jy) if jy else None)
        S.free()
    pickle.dump(out, open(f"logs/s4t/rooms_{stage}.pkl", "wb"))
print("saved")
