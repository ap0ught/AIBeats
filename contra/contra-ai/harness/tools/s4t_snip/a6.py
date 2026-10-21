import importlib, sys, json
sys.path.insert(0, "tools")
import s4t_lab as L
importlib.reload(L)

# calibration: where does the centre pellet arrive (x, y at timer 1) for presses in different motion states
def run(spec, n=130, st="s4/q0/room3"):
    return L.trace(e, st, L.spec_rows(n, spec))

def report(name, spec, press_rows, n=130):
    tr = run(spec, n)
    out = []
    for r in press_rows:          # row index r -> result state tr[r + 1]
        a, b = tr[r], tr[r + 1]
        new = [x for x in bc.bullets(b) if x[2] == 21]
        if not new:
            out.append((r, "no bullet"))
            continue
        sl = new[0][0]
        # follow the slot to timer 1
        arr = None
        for j in range(r + 2, r + 26):
            bb = {x[0]: x for x in bc.bullets(tr[j])}
            if sl in bb and bb[sl][2] == 1 and bb[sl][3] == 1:
                arr = (j - (r + 1), bb[sl][4], bb[sl][5])
        out.append((r, "xb", a["x"], "xa", b["x"], "yb", a["y"], "aim", b["aim"], "j", b["jump"], "n", len(new), "spawn", (new[0][4], new[0][5]), "arr", arr))
    print(name)
    for o in out:
        print("   ", o)

B = lambda r: (r, r + 1, "B")
# ground, still, facing right (after landing at 180)
report("ground still R", [B(60), B(90)], [60, 90])
# ground, moving left continuously from row 52
report("ground moving L", [(52, 125, "Left"), B(60), B(67), B(74), B(81), B(88), B(95), B(102)], [60, 67, 74, 81, 88, 95, 102])
# ground, moving right
report("ground moving R", [(52, 80, "Right"), B(60), B(67), B(74)], [60, 67, 74])
# ground: left 10 frames then still (facing left)
report("ground still L", [(52, 61, "Left"), B(70), B(100)], [70, 100])
# first frame of a move (press on the same row as a new Left)
report("ground first frame of L", [(60, 63, "Left"), B(60)], [60])
report("ground second frame of L", [(60, 63, "Left"), B(61)], [61])
report("ground stop frame after L", [(56, 59, "Left"), B(60)], [60])
# air: no drift, drift left, drift right at rows 13..16 and 38..45
report("air no drift", [B(13), B(40), B(45)], [13, 40, 45])
report("air drift L (tap 1-2)", [(1, 2, "Left"), B(13), B(40), B(45)], [13, 40, 45])
report("air drift R (tap 1-2)", [(1, 2, "Right"), B(13), B(40), B(45)], [13, 40, 45])
report("air drift L tap on the press row", [(13, 14, "Left"), B(13)], [13])
report("air drift L held", [(1, 48, "Left"), B(13), B(40), B(45)], [13, 40, 45])
# crouch still facing right / facing left
report("crouch R", [(58, 70, "Down"), B(60)], [60])
report("crouch L", [(52, 55, "Left"), (58, 70, "Down"), B(60)], [60])
