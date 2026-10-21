"""Skip the sixth Hornhead (2026-10-03): it spawns when the vertical camera reaches 4096, which our camera (13 px
behind the TAS's after the sinking-platform launch) does not before the TAS fights it. So from the exact TAS 2128
state, do not wait for it: walk right after the landing, double-tap sprint shortly before x 286 (the sprint speed
only carries into a jump within ~12 frames of the tap) and dash-jump onto the sinking platform as the TAS does at
2245, matching one of its mid-air frames exactly, then replay its inputs to the landing at 2284.
    python l12h6skip.py   -> knowledge/l12_h6skip.json (inputs from R2_j2128), bookmark H6_j2284"""
import json, resync
from toads.emulator import BizHawk
TAS = ["+".join(t) for t in resync.TAS]; rows = resync.rows
e = BizHawk(log_name="h6skip.log"); e.load("R2_j2128")
root = e.msave()
idx = {rows[j][1:5]: j for j in range(2246, 2284)}
best = None
def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x3B5])
for w in range(0, 27):
    for walk in range(0, 50, 1):
        if w + walk > 60: continue
        e.mload(root); e.step((), w); e.step(("Right",), walk); s0 = e.msave()
        for sprint in ("|Right||Right", "||Right||Right", "|Right|||Right"):
            for jx in (283, 284, 285, 286):
                for gap in ("|",):
                    for k in (22, 23, 24):
                        e.mload(s0); seq = [""] * w + ["Right"] * walk
                        def st(b):
                            e.step(tuple(v for v in b.split("+") if v), 1); seq.append(b); return e.ram(0, 0x800)
                        for b in sprint.split("|"): st(b)
                        m = e.ram(0, 0x800); n = 0
                        while key(m)[0] < jx and n < 12: m = st("Right"); n += 1
                        if key(m)[0] != jx: continue
                        if gap: st("")
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
                        print(f"w {w} walk {walk} {sprint} jump at {jx} gap '{gap}' A {k}: match TAS {hit} after {len(seq) - (2284 - hit)} frames -> end {key(m)} plat {plat} {'OK' if ok else ''}", flush=True)
                        if ok and (best is None or len(seq) < len(best)):
                            best = list(seq)
                            json.dump({"bookmark": "R2_j2128", "j0": 2128, "jend": 2284, "inputs": best}, open("knowledge/l12_h6skip.json", "w"))
                            e.mload(root)
                            for b in best: e.step(tuple(v for v in b.split("+") if v), 1)
                            e.save("H6_j2284")
                            print(f"SAVED {len(best)} frames (TAS 2128->2284 took 156)", flush=True)
        e.mfree(s0)
    if best: break
e.close()
