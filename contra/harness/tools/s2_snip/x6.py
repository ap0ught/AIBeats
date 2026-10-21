# landing table: pellet landing X (at timer 1) vs player X, standing facing right / left, and crouch
import json
e.mload(G["s2_0"]); e.trace(False)
e.step((), 34)            # landed at x=112
st = e.msave()
blob = e.cmd(f"save {bc.STATES_DIR if hasattr(bc,'STATES_DIR') else 'states'}/s2/tmp_land.State")
def job(emu, px):
    emu.load("s2/tmp_land")
    emu.trace(False)
    res = {}
    for mode in ("R", "L", "C"):
        emu.load("s2/tmp_land")
        x = 112
        # walk so that the final approach direction sets the facing
        if mode == "R":
            tgt = px
            if px <= x:
                emu.step(("Left",), x - px + 3); emu.step(("Right",), 3)
            else:
                emu.step(("Right",), px - x)
        elif mode == "L":
            if px >= x:
                emu.step(("Right",), px - x + 3); emu.step(("Left",), 3)
            else:
                emu.step(("Left",), x - px)
        else:
            if px >= x: emu.step(("Right",), px - x)
            else: emu.step(("Left",), x - px)
            emu.step(("Down",), 2)
        s = emu.step(("Down", "B") if mode == "C" else ("B",), 2)
        if s["x"] != px:
            res[mode] = ("badx", s["x"]); continue
        emu.trace(True)
        emu.step(("Down",) if mode == "C" else (), 19)
        tr = emu.last_trace
        emu.trace(False)
        s = tr[-1]
        b = bc.bullets(s)
        res[mode] = [(t, x_, y_) for i, sl, t, r, x_, y_ in b] + [s["death"], s["frame_fc"]]
    return (px, res)
import os
os.makedirs("states/s2", exist_ok=True)
pxs = list(range(48, 209, 4))
out = bc.pmap(E, job, pxs)
for px, res in out:
    print(px, {m: ([v[k][1] for k in range(5)] + [v[0][2], v[0][0]] if isinstance(v, list) else v) for m, v in res.items()})
json.dump(out, open("logs/s2/landing_table.json", "w")) if os.path.isdir("logs/s2") else None
