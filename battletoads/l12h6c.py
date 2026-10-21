"""After our Hornhead-6 kill (bookmark F6_kill, TAS 2129-seg index 90; 2026-10-03): land from the kick, step back,
double-tap and dash-jump (release, Right+A within ~12 frames of the tap) from x 286 so that one of the TAS's mid-air
frames 2246..2283 is matched exactly; then its inputs to the 2284 landing on the sinking platform.
    python l12h6c.py -> knowledge/l12_h6c.json (inputs from F6_kill), bookmark H6_j2284"""
import json, resync
from toads.emulator import BizHawk
TAS = ["+".join(t) for t in resync.TAS]; rows = resync.rows
e = BizHawk(log_name="h6c.log"); e.load("F6_kill")
pre = []
m = e.ram(0, 0x800)
while m[0x475] != 0:
    e.step((), 1); pre.append(""); m = e.ram(0, 0x800)
print("landed from the kick after", len(pre), "idle frames at", (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x3B5], m[0x565]), flush=True)
root = e.msave()
idx = {rows[j][1:5]: j for j in range(2246, 2284)}
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5])
best = None
for w in range(0, 20):
    for back in range(0, 26):
        for w2 in (0, 1, 2, 4):
            e.mload(root); e.step((), w); e.step(("Left",), back); e.step((), w2); s0 = e.msave()
            for sprint in ("|Right||Right", "||Right||Right", "|Right|||Right", "Right||Right", "Right|||Right"):
                for jx in (283, 284, 285, 286):
                    for k in (22, 23, 24):
                        e.mload(s0); seq = list(pre) + [""] * w + ["Left"] * back + [""] * w2
                        def st(b):
                            e.step(tuple(v for v in b.split("+") if v), 1); seq.append(b); return e.ram(0, 0x800)
                        for b in sprint.split("|"): st(b)
                        m = e.ram(0, 0x800); n = 0
                        while key(m)[0] < jx and n < 12: m = st("Right"); n += 1
                        if key(m)[0] != jx: continue
                        st("")
                        hit = None
                        for i in range(k + 40):
                            m = st("Right+A" if i < k else "Right")
                            if m[0x51A] < 47 or (m[0x475] == 0 and i > 5): break
                            j = idx.get(key(m))
                            if j: hit = j; break
                        if not hit: continue
                        for s in range(hit + 1, 2285): m = st(TAS[s])
                        plat = sorted((m[0x3FD+q] | m[0x3EE+q] << 8, m[0x439+q]) for q in range(2, 15) if m[0x3C1+q] == 0x36)
                        ok = key(m) == rows[2284][1:5] and plat == [(128, 234), (416, 78)] and m[0x51A] == 47
                        print(f"w {w} back {back} w2 {w2} {sprint} jump at {jx} A {k}: match TAS {hit}, {len(seq)} frames -> end {key(m)} plat {plat} camy {m[0x89] | m[0x8A] << 8} {'OK' if ok else ''}", flush=True)
                        if ok and (best is None or len(seq) < len(best)):
                            best = list(seq)
                            json.dump({"bookmark": "F6_kill", "jend": 2284, "inputs": best}, open("knowledge/l12_h6c.json", "w"))
                            e.mload(root)
                            for b in best[len(pre):]: e.step(tuple(v for v in b.split("+") if v), 1)
                            e.save("H6_j2284")
                            print(f"SAVED {len(best)} frames from the kill (the TAS: kill 2244 -> 2284 = 40)", flush=True)
            e.mfree(s0)
    if best: break
e.close()
