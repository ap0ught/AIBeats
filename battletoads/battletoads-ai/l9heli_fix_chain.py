"""Replay a join bookmark + the old inputs (L9c 8280..9987) with repairs (edits json = list of {A, TGT, inputs}) applied, lag-aware (an input
is held until the frame counter ticks), comparing the toad's track with the old run at the same OLD index.  Reports the first difference,
the first health/level difference, the raw frame count, and optionally writes the complete raw input list.
    python l9heli_fix_chain.py <bookmark> <edits json or -> [out inputs json]"""
import json, sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
BM = sys.argv[1]; EDITS = json.load(open(sys.argv[2])) if len(sys.argv) > 2 and sys.argv[2] != "-" else []
e = BizHawk(log_name="l9heli_fix_chain.log"); e.load(BM)
t = e.byte(0x0B); raw = []; first = None; hpd = None; lags = 0; nd = 0
def lstep(b):
    global t, lags
    for _ in range(8):
        e.step(bt(b), 1); raw.append(b); m = e.ram(0, 0x800)
        if m[0x0B] != t: break
        lags += 1
    t = m[0x0B]; return m
def okin(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10])
k = 8279; marks = {}
while k < 9987:
    ed = [x for x in EDITS if x["A"] == k]
    if ed:
        for b in ed[0]["inputs"]: e.step(bt(b), 1); raw.append(b)
        k = ed[0]["TGT"]; m = e.ram(0, 0x800); t = m[0x0B]
        ref = bytes(R[OFF + k - 1]); print(f"edit A {ed[0]['A']} -> TGT {k}: toad equal to old: {okin(m) == okin(ref)} (raw {len(raw)})", flush=True)
        continue
    if 9650 <= k: 
        e.step(bt(ins[OFF + k]), 1); raw.append(ins[OFF + k]); m = e.ram(0, 0x800); t = m[0x0B]     # (the death freeze: no lag logic)
    else:
        m = lstep(ins[OFF + k])
    k += 1; ref = bytes(R[OFF + k - 1])
    if okin(m) != okin(ref):
        nd += 1
        if first is None: first = k; print("first track diff at old index", k, "ours", okin(m), "old", okin(ref), "| ours", ostr(m), "| old", ostr(ref), flush=True)
        if hpd is None and okin(m)[3:] != okin(ref)[3:]: hpd = k; print("first hp/level diff at", k, okin(m), okin(ref), flush=True)
print(f"raw frames {len(raw)} (old 1708), lag frames {lags}, diff frames {nd}, first {first}, hp/level {hpd}, end level {m[0x10]} {tstr(m)}", flush=True)
if len(sys.argv) > 3: json.dump(raw, open(sys.argv[3], "w"))
e.close()
