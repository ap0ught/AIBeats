"""Two-blow kill (2026-10-03): a blow that STUNS (the enemy's state byte 64), then once it has landed a dash run-up and
direction+B - the boot (anim 31) - which kills whatever its health. Scan both from a bookmark.
    python stunboot.py <bookmark> <ids hex> [out]  -> knowledge/stunboot_<out>.json (inputs from the bookmark), prints the kill frame"""
import itertools, json, sys
from toads.emulator import BizHawk
from fightbeam import foes, tx, th, expand, LEADS, toward
bm, ids = sys.argv[1], {int(v, 16) for v in sys.argv[2].split(",")}
out = sys.argv[3] if len(sys.argv) > 3 else bm
e = BizHawk(log_name=f"stunboot_{out}.log"); e.load(bm); base = e.msave()
m = e.ram(0, 0x800); lives0 = m[0x11]
def foe(m):
    for q in range(2, 15):
        if m[0x3C1 + q] in ids: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q], m[0x4B1 + q])
def hurt(m): return m[0x51A] < 40 or m[0x11] < lives0
stuns = []
for w in range(0, 90, 2):
    e.mload(base); e.step((), w); m = e.ram(0, 0x800)
    if hurt(m) or not foe(m): continue
    t = toward(m, ids); ws = e.msave(); hp = foe(m)[2]
    for lead in LEADS:
        e.mload(ws); seq = expand(lead, t)
        for x in seq: e.step(tuple(v for v in x.split("+") if v), 1)
        for k in range(40):
            m = e.ram(0, 0x800); f = foe(m)
            if hurt(m) or not f: break
            if f[2] < hp and f[3] == 64:
                stuns.append((w + len(seq) + k, w, lead, e.msave(), f)); break
            e.step((), 1)
stuns.sort(key=lambda s: s[0])
print(f"{len(stuns)} stunning blows; earliest {[(s[0], s[1], s[2]) for s in stuns[:4]]}", flush=True)
best = None
for t0, w, lead, sid, f in stuns[:12]:
    if best and t0 > best[0]: break
    for w2, taps, run in itertools.product(range(8, 60, 2), ("d", "t"), (4, 6, 8, 10, 12, 14)):
        if best and t0 + w2 + run + 30 >= best[0]: continue
        e.mload(sid); e.step((), w2); m = e.ram(0, 0x800); g = foe(m)
        if not g or hurt(m): continue
        t = toward(m, ids); pre = [t, "", t, "", t, ""] if taps == "t" else [t, ""]
        seq = pre + [t] * run + [t + "+B"]
        for x in seq: e.step(tuple(v for v in x.split("+") if v), 1)
        for k in range(45):
            m = e.ram(0, 0x800); g = foe(m)
            if hurt(m): break
            if g is None or g[2] == 0:
                tot = t0 + w2 + len(seq) + k + 1
                if best is None or tot < best[0]:
                    best = (tot, w, lead, w2, taps, run)
                    print(f"KILL at {tot}: stun ({w}, {lead!r}) boot after {w2} ({taps}, run {run})", flush=True)
                break
            e.step((), 1)
if best:
    tot, w, lead, w2, taps, run = best
    e.mload(base); e.step((), w); m = e.ram(0, 0x800); t = toward(m, ids)
    ins = [""] * w + expand(lead, t)
    for x in expand(lead, t): e.step(tuple(v for v in x.split("+") if v), 1)
    while True:
        m = e.ram(0, 0x800); f = foe(m)
        if f[3] == 64: break
        e.step((), 1); ins.append("")
    e.step((), w2); ins += [""] * w2; m = e.ram(0, 0x800); t = toward(m, ids)
    pre = [t, "", t, "", t, ""] if taps == "t" else [t, ""]
    seq = pre + [t] * run + [t + "+B"]
    for x in seq: e.step(tuple(v for v in x.split("+") if v), 1)
    ins += seq
    while True:
        m = e.ram(0, 0x800); g = foe(m)
        if g is None or g[2] == 0: break
        e.step((), 1); ins.append("")
    json.dump(ins, open(f"knowledge/stunboot_{out}.json", "w")); e.save(f"stunboot_{out}_end")
    print(f"saved knowledge/stunboot_{out}.json: {len(ins)} frames from {bm}; toad {tx(m)},{th(m)}", flush=True)
else:
    print("no two-blow kill found", flush=True)
e.close()
