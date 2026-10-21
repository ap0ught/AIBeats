"""Corridor by the TAS's inputs from the matched entry (L9X_corrb = TAS 59565 state (584,70, speed 80)), with a wait first so the patrolling
mine sits elsewhere. Reports waits that get through (x >= 1115 unhurt) and saves the shortest. -> knowledge/l9_corr_tas.json, bookmark L9T_exit"""
import json, re
from toads.emulator import BizHawk
rows = {}
for l in open("tas/watch_1p_log.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", l)
    if m: r = tuple(int(v) for v in m.groups()); rows[r[0]] = r
tas = json.load(open("knowledge/tas1p_l9_inputs.json")); ANCHOR = 51652; T0 = 59565
def legal(b): return tuple(v for v in b.split("+") if v and not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
def st(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x565])
e = BizHawk(log_name="l9tas2.log"); e.load("L9X_corrb"); base = e.msave(); best = None
for w in range(0, 700, 5):
    e.mload(base); e.step((), w); ins = [""] * w; hurt = None; out = None
    for t in range(T0 + 1, 59990):
        b = legal(tas[t - ANCHOR]); e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800); r = rows.get(t)
        if r and r[3] == 0 and rows[t - 1][3] != 0:
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
        if m[0x51A] < 31 or m[0x11] < 3: hurt = t; break
        if (m[0x3FD] | m[0x3EE] << 8) >= 1115 and out is None: out = t
        if out and t > out + 30: break
    s = st(m)
    if out and not hurt: print(f"wait {w}: THROUGH at TAS {out}, end {s}, {len(ins)} frames", flush=True)
    elif w % 50 == 0: print(f"wait {w}: hurt {hurt} at x {s[0]}", flush=True)
    if out and not hurt and (best is None or len(ins) < best[0]):
        best = (len(ins), w); e.save("L9T_exit"); json.dump({"bookmark": "L9X_corrb", "wait": w, "inputs": ins}, open("knowledge/l9_corr_tas.json", "w"))
print("best", best, flush=True); e.close()
