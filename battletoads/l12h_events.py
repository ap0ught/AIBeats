"""L12h track: event list from a per-frame RAM dump (logs/fix/<tag>.ram) of a tower segment.
    python l12h_events.py <tag> <segment>"""
import json, sys
from toads.emulator import LOGS_DIR
tag, seg = sys.argv[1], sys.argv[2]
buf = open(LOGS_DIR / "fix" / f"{tag}.ram", "rb").read(); N = len(buf) // 2048
ins = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))["inputs"]]
def row(i): return buf[i * 2048:(i + 1) * 2048]
def toad(m): return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], cam=m[0x89] | m[0x8A] << 8, t=m[0x0B], spd=m[0x565])
def objs(m): return [(m[0x3C1 + q], m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8, m[0x51A + q], q) for q in range(2, 15) if m[0x3C1 + q]]
prev = None; pobj = {}; idle0 = None; out = []
for i in range(N):
    m = row(i); s = toad(m); o = objs(m)
    if m[0x10] != 5: 
        if prev and prev.get("lvl") == 5: out.append((i, f"LEVEL byte -> {m[0x10]}"))
        s["lvl"] = m[0x10]; prev = s; continue
    s["lvl"] = 5
    ids = {}
    for (d, x, H, hp, q) in o: ids.setdefault(d, []).append((x, H, hp, q))
    if prev and prev.get("lvl") == 5:
        if prev["z"] != 0 and s["z"] == 0: out.append((i, f"land x={s['x']} H={s['H']} cam={s['cam']} t={s['t']}"))
        if prev["an"] not in (94, 95, 96) and s["an"] in (94, 95, 96): out.append((i, f"POLE grab x={s['x']} H={s['H']} cam={s['cam']}"))
        if prev["an"] in (94, 95, 96) and s["an"] not in (94, 95, 96): out.append((i, f"POLE leave x={s['x']} H={s['H']}"))
        for d in (0x60, 0x5c, 0x62):
            a = len(pobj.get(d, [])); b = len(ids.get(d, []))
            if b > a: out.append((i, f"SPAWN {d:02x} {ids[d]} cam={s['cam']} toad=({s['x']},{s['H']})"))
            if b < a: out.append((i, f"GONE  {d:02x} cam={s['cam']} toad=({s['x']},{s['H']})"))
        for d in (0x5c, 0x62):
            for (x, H, hp, q) in ids.get(d, []):
                for (x0, H0, hp0, q0) in pobj.get(d, []):
                    if q0 == q and hp < hp0: out.append((i, f"HIT {d:02x} hp {hp0}->{hp} toad=({s['x']},{s['H']}) an={s['an']}"))
        a61 = len(pobj.get(0x61, [])); b61 = len(ids.get(0x61, []))
        if a61 == 0 and b61 > 0: out.append((i, "wind bubbles start"))
        if a61 > 0 and b61 == 0: out.append((i, "wind bubbles end"))
    pobj = ids; prev = s
# idle stretches in the inputs
i = 0
while i < len(ins):
    if ins[i] == "":
        j = i
        while j < len(ins) and ins[j] == "": j += 1
        if j - i >= 12: out.append((i, f"IDLE {j - i} frames (to {j})"))
        i = j
    else: i += 1
out.sort()
for f, t in out: print(f, t)
