"""L12h track: event list of the 1-player TAS's Level 12 (tas/watch_1p_l12.txt), frames relative to its placement (69603)."""
import re
T0 = 69603
prev = None; pobj = {}; pan = None; pz = None
for l in open("tas/watch_1p_l12.txt"):
    if " x=" not in l: continue
    f = int(l.split()[0][1:])
    if f < T0: continue
    mm = re.search(r" x=(-?\d+) h=(-?\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+) cp=(\d+) p1=(\S+)", l)
    x, h, z, st, an, hp, cam, camy = map(int, mm.groups()[:8]); p1 = mm.group(10)
    o = l.split("|")[1].split() if "|" in l else []
    ids = {}
    for t in o:
        d, r = t.split(":"); v = r.split(",")
        if len(v) < 3 or not v[2]: continue
        ids.setdefault(d, []).append((int(v[0]), int(v[1]), int(v[2])))
    r = f - T0
    if prev is not None:
        if pz != 0 and z == 0: print(r, f"land x={x} h={h} cam={camy}")
        if pan not in (94, 95, 96) and an in (94, 95, 96): print(r, f"POLE grab x={x} h={h} cam={camy}")
        if pan in (94, 95, 96) and an not in (94, 95, 96): print(r, f"POLE leave x={x} h={h}")
        for d in ("60", "5c", "62"):
            a = pobj.get(d, []); b = ids.get(d, [])
            if len(b) > len(a): print(r, f"SPAWN {d} {b} cam={camy} toad=({x},{h})")
            if len(b) < len(a): print(r, f"GONE  {d} cam={camy} toad=({x},{h})")
            if len(a) == len(b):
                for (x0, h0, hp0), (x1, h1, hp1) in zip(a, b):
                    if hp1 < hp0: print(r, f"HIT {d} hp {hp0}->{hp1} toad=({x},{h}) an={an} p1={p1}")
        if ("61" in ids) != ("61" in pobj): print(r, "wind bubbles", "start" if "61" in ids else "end")
        if ("le" in p1 and "ri" in p1) or ("up" in p1 and "do" in p1): print(r, "BANNED", p1, f"toad=({x},{h}) z={z}")
    prev = 1; pobj = ids; pan = an; pz = z
