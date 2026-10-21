"""Face 4 without the pole (2026-10-03): launch early onto the small platform (l12_lap_launch), jump into the wind and
land on the ring ledge at h 5022; wait on the ledge until the face is gone, then dash LEFT to meet the old run's dash
along that ledge (old frames 9680..9800) exactly.    python l12lap3.py -> knowledge/short_L12lap.json"""
import json
from toads.emulator import BizHawk, LOGS_DIR
from shortcut import k5
d = json.load(open(LOGS_DIR / "pbeam_L12a.json")); old = [b.replace(",", "+") for b in d["inputs"]]
launch = json.load(open("knowledge/l12_lap_launch.json"))
e = BizHawk(log_name="l12lap3.log")
e.load(d["bookmark"])
for b in old[:9680]: e.step(tuple(x for x in b.split("+") if x), 1)
targets = {}
for i, b in enumerate(old[9680:9800]):
    e.step(tuple(x for x in b.split("+") if x), 1); m = e.ram(0, 0x800)
    if m[0x475] == 0: targets.setdefault(k5(m), 9680 + i + 1)
print("old ledge states:", len(targets), sorted(k[0] for k in targets)[:5], "...", flush=True)
e.load("L12_lap"); ins = []
def st(b, n=1):
    for _ in range(n):
        e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b)
    return e.ram(0, 0x800)
for b in launch: st(b)
st("", 40); m = st("Right+A", 68)
print("on the ledge:", k5(m), "frame", 8616 + len(ins), flush=True)
quiet = 0
st("Left"); st(""); m = st("Left")                               # dash left against the wind: the ledge is not a full ring
while quiet < 30 and len(ins) < 1200:
    m = st("Left")
    if (m[0x439] | m[0x42A] << 8) != 5022 or m[0x11] < 6:
        print("fell off the ledge at frame", 8616 + len(ins), k5(m)); break
    quiet = quiet + 1 if not any(m[0x3C1 + s] in (0x60, 0x61) for s in range(2, 15)) else 0
print("wind gone at frame", 8616 + len(ins), "toad", k5(m), flush=True)
base = e.msave(); n0 = len(ins)
frontier = [(e.msave(), [])]; seen = set(); goal = None
for depth in range(1, 400):
    new = []
    for sid, path in frontier:
        for act in ("", "Left", "Right"):
            e.mload(sid); e.step(tuple(v for v in act.split("+") if v), 1); m = e.ram(0, 0x800)
            if m[0x51A] < 40 or m[0x11] < 6: continue
            k = k5(m); kk = k + (m[0x3B5], m[0x457])
            if kk in seen: continue
            seen.add(kk)
            if k in targets:
                goal = (depth, path + [act], targets[k], k); break
            new.append((e.msave(), path + [act], 0 if k[1] == 5022 else 50))
        if goal: break
    for sid, _ in frontier: e.mfree(sid)
    if goal: break
    new.sort(key=lambda n: n[2]); frontier = [(s, p) for s, p, _ in new[:300]]
    for s, _, _ in new[300:]: e.mfree(s)
if goal:
    depth, path, j, k = goal
    piece = ins + path
    print(f"joins the old run at {j} after {len(piece)} frames (old {j - 8616}): saves {j - 8616 - len(piece)}", flush=True)
    json.dump({"segment": "L12a", "a": 8616, "b": j, "inputs": piece}, open("knowledge/short_L12lap.json", "w"))
else:
    print("no join found")
e.close()
