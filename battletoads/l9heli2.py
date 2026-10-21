"""The helicopter creature (0x70) intercepts the TAS's fall; scan an idle k at our standing state (L9c index 7852 = TAS 59328, (813,102))
before the TAS's inputs so the creature's phase differs; keep runs that reach TAS 59565 unhurt. -> knowledge/l9_heli.json, bookmark L9H_end"""
import json, re
from toads.emulator import BizHawk, LOGS_DIR
rows = {}
for l in open("tas/watch_1p_log.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", l)
    if m: r = tuple(int(v) for v in m.groups()); rows[r[0]] = r
tas = json.load(open("knowledge/tas1p_l9_inputs.json")); ANCHOR = 51652
seg = json.load(open(LOGS_DIR / "pbeam_L9c.json")); ours = [x.replace(",", "+") for x in seg["inputs"]]
def legal(b): return tuple(v for v in b.split("+") if v and not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
def st(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x565], m[0x3B5])
def heli(m): return [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q]) for q in range(2, 15) if m[0x3C1 + q] == 0x70]
F, T0 = 7852, 59328
e = BizHawk(log_name="l9heli2.log"); e.load(seg["bookmark"])
for b in ours[:F]: e.step(tuple(v for v in b.split("+") if v), 1)
base = e.msave(); m = e.ram(0, 0x800); print("base", st(m), "heli", heli(m), flush=True)
best = None
for k in range(0, 240, 2):
    e.mload(base); e.step((), k); ins = [""] * k; hurt = None; land = None; grab = None
    for t in range(T0 + 1, 59566):
        b = legal(tas[t - ANCHOR]); e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800); r = rows[t]
        if r[3] == 0 and rows[t - 1][3] != 0:
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
        if grab is None and m[0x3B5] in (36, 37): grab = t
        if land is None and t >= 59430 and m[0x475] == 0 and m[0x439] == 38: land = t
        if m[0x51A] < 47 or m[0x11] < 3: hurt = t; break
    s = st(m)
    ok = not hurt and land and abs(s[0] - 584) <= 6 and s[1] == 70
    if k % 20 == 0 or ok or (land and not hurt): print(f"k {k}: hurt {hurt} grab {grab} landed {land} end {s} {'OK' if ok else ''}", flush=True)
    if ok and (best is None or len(ins) < best[0]):
        best = (len(ins), k); e.save("L9H_end"); json.dump({"segment": "L9c", "from": F, "wait": k, "tas_t0": T0, "inputs": ins, "end_state": s}, open("knowledge/l9_heli.json", "w"))
print("best", best, flush=True); e.close()
