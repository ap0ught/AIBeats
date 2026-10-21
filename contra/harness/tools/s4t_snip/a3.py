import importlib, sys, json
sys.path.insert(0, "tools")
import s4t_lab as L
importlib.reload(L)

# (i)-(ii) hop steering in stage 4 room 3 (state = T0)
def xs(spec, n=70, st="s4/q0/room3"):
    tr = L.trace(e, st, L.spec_rows(n, spec))
    return tr

for name, spec in (("none", []), ("L tap T1-2", [(1, 2, "Left")]), ("L hold 1-60", [(1, 60, "Left")]),
                   ("R tap 1-2", [(1, 2, "Right")]), ("L 1-10 then R 11-30", [(1, 10, "Left"), (11, 30, "Right")]),
                   ("L tap 20-21", [(20, 21, "Left")]), ("L row0-1", [(0, 1, "Left")]),
                   ("L 1-2, R 8-9", [(1, 2, "Left"), (8, 9, "Right")]),
                   ("L 1-2, L 8-9", [(1, 2, "Left"), (8, 9, "Left")])):
    tr = xs(spec)
    print(name, "x:", [tr[i]["x"] for i in range(0, 62, 3)], "y@", [tr[i]["y"] for i in (1, 13, 17, 26, 37, 50, 51)], "land", next(i for i in range(2, 70) if tr[i]["jump"] == 0),
          "aim", [tr[i]["aim"] for i in (1, 5, 30, 55)])

# (v) walking while firing after landing: Left held from row 52, B every 5 frames (2-frame holds)
spec = [(52, 120, "Left")] + [(55 + 5 * k, 56 + 5 * k, "B") for k in range(8)]
tr = xs(spec, 125)
print("walk+fire x:", [(i, tr[i]["x"]) for i in range(50, 100, 2)])
for i in range(55, 80):
    s = tr[i]
    print(i, "x", s["x"], "aim", s["aim"], "pad", hex(s["pad"]), bc.fmt_bullets(s))
print("hits", L.hits(tr))
