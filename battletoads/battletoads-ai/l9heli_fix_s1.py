"""S1: get past the two propeller bugs (0x74 at x 824/840, h 128-135) without being grabbed (anim 36/37), like the record does
(jump over them).  Root = L9c 7819 (standing on the upper step (756,134), sprint primed).  Pattern: Right x k, idle x pre,
Right+A x a, then Right.  Report the first frame with x >= 848 (past both bugs, over the shaft) and the state there.
-> logs/fix/heli_s1.json, bookmark L9heli_7819"""
import json
from l9heli_fix_lib import *
ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_s1.log")
e.load("L9heli_7800")
for f in range(OFF + 7800, OFF + 7819): e.step(bt(ins[f]), 1)
m = e.ram(0, 0x800); print("7819", tstr(m), "|", ostr(m), flush=True); e.save("L9heli_7819")
root = e.msave(); res = []
for k in range(0, 32):
    for pre in (0, 1):
        for a in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32):
            seq = ["Right"] * k + [""] * pre + ["Right+A"] * a
            seq += ["Right"] * (80 - len(seq))
            e.mload(root); grab = None; past = None; jumped = None; tr = []
            for i, b in enumerate(seq):
                e.step(bt(b), 1); m = e.ram(0, 0x800); s = toad(m)
                if s["an"] in CARRIED: grab = (i + 1, s["x"], s["H"]); break
                if s["hp"] < 47: grab = ("HURT", i + 1, s["x"], s["H"]); break
                if jumped is None and i >= k + pre and s["z"] and m[0x4C0] < 128 and m[0x4C0] > 0: jumped = (i + 1, s["x"], s["H"])
                if 815 <= s["x"] <= 847: tr.append((s["x"], s["H"] - 6400))
                if s["x"] >= 848: past = (i + 1, s["x"], s["H"], s["spd"], m[0x4C0], m[0x4CF]); break
            res.append(dict(k=k, pre=pre, a=a, grab=grab, past=past, jumped=jumped, tr=tr))
            if past: print(f"k {k} pre {pre} a {a}: PAST at {past} jumped {jumped} track {tr[:12]}", flush=True)
json.dump(res, open(LOGS_DIR / "fix" / "heli_s1.json", "w"))
ok = sorted([r for r in res if r["past"]], key=lambda r: (r["past"][0], r["past"][2]))
print("best:", [(r["k"], r["pre"], r["a"], r["past"]) for r in ok[:15]], flush=True)
print("grabbed:", sum(1 for r in res if r["grab"]), "of", len(res), flush=True)
e.close()
