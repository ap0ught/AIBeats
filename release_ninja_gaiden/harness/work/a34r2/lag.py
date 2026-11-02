"""record vs TAS progress by background scroll: python work/a34r2/lag.py <rec json> <TAS control> <TAS end> [step]
prints record t, room, cum scroll, and the TAS t (after control) at which the TAS's scroll (since that room's start)
first reaches the same value -> lag = record t - TAS t."""
import sys, json
sys.path.insert(0, "ng/stages")
import a34_core as K
d = json.load(open(sys.argv[1]))["rows"]; c0, c1 = int(sys.argv[2]), int(sys.argv[3])
step = int(sys.argv[4]) if len(sys.argv) > 4 else 20
tas = []
for f in range(c0, c1):
    r = K.ref_at(f); scr = int(r[0x52]); scr = scr - 256 if scr >= 128 else scr
    tas.append((f - c0, int(r[0x6E]), scr * 256 + int(r[0x51])))
rooms = []
for t, rm, s in tas:
    if not rooms or rooms[-1][0] != rm: rooms.append([rm, t, s])
for ro in rooms[1:]:
    ro[2] = tas[min(ro[1] + 23, len(tas) - 1)][2]
print("TAS rooms", rooms)
out = []
for i, r in enumerate(d):
    if i % step: continue
    ri = r["room"]
    if ri >= len(rooms): continue
    rm, t0, s0 = rooms[ri]
    # first TAS frame with scroll progress >= record's
    tt = next((t for t, rr, s in tas if rr == rm and (s - s0) >= r["scroll"]), None) if r["scroll"] > 0 else None
    print(f"t {r['t']:7.1f} room {ri} scroll {r['scroll']:5d} sx {r['sx']} sy {r['sy']}  TAS t {tt}  lag {None if tt is None else round(r['t'] - tt)}")
