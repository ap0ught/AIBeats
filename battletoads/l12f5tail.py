"""Fight-5 tail (2026-10-03): after the walker dies (piece index 369 = TAS 1984) the TAS sits through the springy
platform's deep sink and is thrown to the floor above (2002), jumps at 2008, Left+A at 2015, lands (34,30) at 2066,
and its camera is at 4119 there -> 4096 at 2102 (which spawns Hornhead 6 - it locks the vertical scroll until
dead, so it must spawn before the fight spot). Our piece walked the floor instead and the camera stuck at 4109.
Scan: wait, A-hold (the throw), then the TAS's floor inputs 2003..2128 after an idle d; keep camy <= 4096 at the
(194,30) landing.   python l12f5tail.py -> knowledge/l12_f5tail.json {from: 369, inputs}, bookmark F5T_end"""
import json, resync
from toads.emulator import BizHawk
TAS = ["+".join(t) for t in resync.TAS]
ins = json.load(open("knowledge/l12_f5_piece.json")); ins = ins["inputs"] if isinstance(ins, dict) else ins
e = BizHawk(log_name="f5tail.log"); e.load("L12_t1kill")
for b in ins[:369]: e.step(tuple(v for v in b.split("+") if v), 1)
base = e.msave()
def H(m): return m[0x439] | m[0x42A] << 8
best = None
for fw in range(0, 44, 1):
    for k in (4, 8, 12, 16, 20, 24, 30):
        for d in (0, 2, 4, 6, 8):
            e.mload(base); seq = []
            def st(b):
                e.step(tuple(v for v in b.split("+") if v), 1); seq.append(b); return e.ram(0, 0x800)
            for b in [""] * fw + ["A"] * k: m = st(b)
            land = None
            for f in range(100):
                if m[0x475] == 0 and H(m) >= 1822: land = len(seq); break
                m = st("")
            if land is None or m[0x51A] < 47: continue
            for _ in range(d): st("")
            ok = True
            for j in range(2003, 2129):
                m = st(TAS[j])
                if m[0x51A] < 47: ok = False; break
                if j == 2066 and (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475]) != (34, 30, 0): ok = False; break
            if not ok: continue
            end = (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475]); cam = m[0x89] | m[0x8A] << 8
            if end == (194, 30, 0):
                print(f"wait {fw} A {k} idle {d}: floor at {1984 + land}, end {end} at {1984 + len(seq)} (TAS 2128) camy {cam}", flush=True)
                if cam <= 4096 and (best is None or len(seq) < len(best)):
                    best = list(seq)
                    json.dump({"from": 369, "jend": 2128, "inputs": best}, open("knowledge/l12_f5tail.json", "w"))
                    e.save("F5T_end"); print(f"SAVED {len(best)} frames from index 369 (the piece had {len(ins) - 369} to 2069 + 59 to 2128 = {len(ins) - 369 + 59})", flush=True)
e.close()
