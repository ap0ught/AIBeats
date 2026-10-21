import importlib, sys, json
sys.path.insert(0, "tools")
import s4t_lab as L
importlib.reload(L)

rep = json.load(open("logs/s4/q0_report.json"))
rows = [tuple(r) for r in json.load(open("logs/s4/q0_rows.json"))]
r2, r3 = rep["rooms"][1], rep["rooms"][2]
base = rows[r2["load"]:r2["load"] + 446]          # up to and including the last press's hold frame
for name, mv in (("stay", []), ("L60", [("Left", 60)]), ("L75", [("Left", 75)]), ("R40", [("Right", 40)]), ("L140", [("Left", 140)])):
    seq = list(base)
    for b, n in mv:
        seq += [(b,)] * n
    seq += [("Up",)] * (720 - len(seq))
    tr = L.trace(e, "s4/q0/room2", seq)
    cl = next(i for i in range(440, 700) if tr[i]["cleared"] == 1)
    nx = next(i for i in range(440, 720) if tr[i]["screen"] != tr[i - 1]["screen"])
    dead = [i for i in range(1, len(tr)) if tr[i]["death"] & 1][:1]
    print(name, "x at clear", tr[cl]["x"], "cleared idx", cl, "new room idx", nx, "x at T0,T1,T2:", tr[nx]["x"], tr[nx + 1]["x"], tr[nx + 2]["x"], "dead", dead,
          "x just before", tr[nx - 1]["x"], "aim", tr[nx + 1]["aim"])
