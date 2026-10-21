"""Hold the old route's tail on our run by one-frame tweaks (2026-10-04). Our run drifts a pixel from the old
route's track (a bubble placed differently in the faces section), and every precise landing after that (platform
edges, dash-jump taps) then breaks. Loop: replay the old inputs from our state; at the first old-route landing we
miss (x, h, z not equal), scan single-frame button replacements in the frames since the previous landing (then
pairs), keep the one that restores the landing exactly and holds the most later landings; repeat.
    python tailfix.py <our bookmark at old frame f0> <f0> [end]  -> knowledge/l12_tail_tweak.json {f0, inputs, tweaks}"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
BTN = ["", "A", "Right", "Right+A", "Left", "Left+A", "B", "Down", "Up"]
bm, f0 = sys.argv[1], int(sys.argv[2]); end = int(sys.argv[3]) if len(sys.argv) > 3 else None
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]
end = end or len(old)
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5])
# the old route's own landings (reference)
e2 = BizHawk(log_name="tailfix_ref.log"); e2.load("L12w_at5011"); ref = {}; pz = 0
for i, b in enumerate(old[5011:end]):
    e2.step(tuple(v for v in b.split("+") if v), 1); m2 = e2.ram(0, 0x800); f = 5011 + i + 1
    if m2[0x475] == 0 and pz > 0 and f > f0: ref[f] = key(m2)
    pz = m2[0x475]
    if m2[0x10] != 5: end = f; break
e2.close()
lands = sorted(ref); print(f"{len(lands)} old landings from {f0} to {end}", flush=True)
e = BizHawk(log_name="tailfix.log"); e.load(bm); root = e.msave()
tweaks = {}
def inputs(): return [tweaks.get(k, old[k]) for k in range(f0, end)]
def play(seq, upto=None):
    """-> list of (f, ok, key) at old landings, hurt frame or None"""
    e.mload(root); out = []; hurt = None
    for k, b in enumerate(seq):
        f = f0 + k + 1
        if upto and f > upto: break
        e.step(tuple(v for v in b.split("+") if v), 1); m = e.ram(0, 0x800)
        if f in ref: out.append((f, key(m)[:3] == ref[f][:3], key(m)[:3]))
        if m[0x51A] < 47 or m[0x11] < 4 or m[0x10] != 5: hurt = f; break
    return out, hurt
guard = 0
while guard < 400:
    guard += 1
    out, hurt = play(inputs())
    bad = next((f for f, ok, k in out if not ok), None)
    if hurt and (bad is None or hurt < bad): bad = hurt
    if bad is None:
        print("ALL LANDINGS HOLD to", end, flush=True); break
    before = sorted(f for f in lands if f < bad)
    prev = before[-2] if len(before) >= 2 else (before[-1] if before else f0)      # two landings back: the pixel is often lost one jump earlier
    prev = max(prev, f0, bad - 120)
    print(f"landing {bad} missed ({[o for o in out if o[0] == bad]}; hurt {hurt}); scanning tweaks in {prev}..{bad - 1} ({len(tweaks)} so far)", flush=True)
    best = None
    for f in range(bad - 1, prev - 1, -1):
        if f in tweaks: continue
        for b in BTN:
            if b == old[f]: continue
            t2 = dict(tweaks); t2[f] = b
            seq = [t2.get(k, old[k]) for k in range(f0, end)]
            o2, h2 = play(seq, upto=min(end, bad + 400))
            okb = next((ok for ff, ok, k in o2 if ff == bad), False)
            if not okb or (h2 and h2 <= bad + 400): continue
            score = sum(1 for ff, ok, k in o2 if ok and ff >= bad)
            if best is None or score > best[0]: best = (score, f, b)
            if score >= sum(1 for ff in lands if bad <= ff <= bad + 400): break
        if best and best[0] >= sum(1 for ff in lands if bad <= ff <= bad + 400): break
    if best is None:
        print("no single tweak restores landing", bad, "- trying pairs", flush=True)
        for f in range(bad - 1, prev - 1, -1):
            for f2 in range(f - 1, max(prev, f - 12) - 1, -1):
                for b in ("", "Right", "Left", "A"):
                    for b2 in ("", "Right", "Left", "A"):
                        t2 = dict(tweaks); t2[f] = b; t2[f2] = b2
                        seq = [t2.get(k, old[k]) for k in range(f0, end)]
                        o2, h2 = play(seq, upto=min(end, bad + 400))
                        okb = next((ok for ff, ok, k in o2 if ff == bad), False)
                        if okb and not (h2 and h2 <= bad + 400):
                            best = (sum(1 for ff, ok, k in o2 if ok and ff >= bad), f, b, f2, b2); break
                    if best: break
                if best: break
            if best: break
    if best is None:
        print("STUCK at landing", bad, flush=True); break
    if len(best) == 3: tweaks[best[1]] = best[2]
    else: tweaks[best[1]] = best[2]; tweaks[best[3]] = best[4]
    print("   tweak", best[1:], "-> holds", best[0], "later landings", flush=True)
    json.dump({"f0": f0, "inputs": inputs(), "tweaks": {str(k): v for k, v in tweaks.items()}, "upto": bad}, open("knowledge/l12_tail_tweak.json", "w"))
json.dump({"f0": f0, "inputs": inputs(), "tweaks": {str(k): v for k, v in tweaks.items()}, "end": end}, open("knowledge/l12_tail_tweak.json", "w"))
e.close()
