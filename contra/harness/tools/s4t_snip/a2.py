import importlib, sys, json
sys.path.insert(0, "tools")
import s4t_lab as L
importlib.reload(L)

rep = json.load(open("logs/s4/q0_report.json"))
rows = [tuple(r) for r in json.load(open("logs/s4/q0_rows.json"))]
r2, r3, r4 = rep["rooms"][1], rep["rooms"][2], rep["rooms"][3]
print("room2 load", r2["load"], "last hit T", r2["last_hit_T"], "next_T", r2["next_T"], "room3 load", r3["load"])
seg = rows[r2["load"]:r3["load"] + 70]
tr = L.trace(e, "s4/q0/room2", seg)
n2 = r3["load"] - r2["load"]
# around the last hit, the clear and the walk-in
for i in range(r2["last_hit_T"] - 25, n2 + 62):
    s = tr[i]
    if i < r2["last_hit_T"] + 3 or s["cleared"] != tr[i - 1]["cleared"] or s["screen"] != tr[i - 1]["screen"] or i > n2 - 3 or i % 10 == 0 or s["y"] != tr[i-1]["y"] or s["x"] != tr[i-1]["x"]:
        print(f"i{i:4d} in={'+'.join(seg[i - 1]) if i else '':10s} x{s['x']:4d} y{s['y']:4d} j{s['jump']:3d} aim{s['aim']} cl{s['cleared']:3d} scr{s['screen']} cores{s['cores']} adv{s['adv']} ps{s['pstate']} tr{s['trans']} isc{s['iscroll']} B[{bc.fmt_bullets(s)}]")
