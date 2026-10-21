import importlib, sys, json
sys.path.insert(0, "tools")
import s4t_lab as L
importlib.reload(L)

rep = json.load(open("logs/s4/q0_report.json"))
rows = [tuple(r) for r in json.load(open("logs/s4/q0_rows.json"))]
r2, r3 = rep["rooms"][1], rep["rooms"][2]
base = rows[r2["load"]:r2["load"] + 522]          # up to the frame cleared reads 1
# Up from 522 as in the run, plus B every 5 frames from 500 on
seq = list(base) + [("Up",)] * 220
for k in range(500, len(seq) - 1, 5):
    seq[k] = tuple(set(seq[k]) | {"B"})
    seq[k + 1] = tuple(set(seq[k + 1]) | {"B"})
tr = L.trace(e, "s4/q0/room2", seq)
nx = next(i for i in range(440, len(tr)) if tr[i]["screen"] != tr[i - 1]["screen"])
print("new room idx", nx)
for i in range(498, len(tr)):
    s = tr[i]
    nb = len(bc.bullets(s))
    if nb or i % 10 == 0 or abs(i - nx) < 4:
        print(i, "T", i - nx, "in", "+".join(seq[i - 1]), "x", s["x"], "y", s["y"], "cl", s["cleared"], "pad", hex(s["pad"]), "nb", nb, bc.fmt_bullets(s)[:90])
