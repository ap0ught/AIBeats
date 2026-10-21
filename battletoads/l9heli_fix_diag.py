"""Diagnose a join bookmark + edits: lag-aware replay of the old inputs, printing the first frames where the toad's exact state
(x, sub-x, H, air, speed, $466, hp) differs from the old run's and every lag frame.   python l9heli_fix_diag.py <bookmark> <edits|-> <stop> [show n]"""
import json, sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
BM = sys.argv[1]; EDITS = json.load(open(sys.argv[2])) if sys.argv[2] != "-" else []; STOP = int(sys.argv[3]); SHOW = int(sys.argv[4]) if len(sys.argv) > 4 else 12
import os; FULL = bool(os.environ.get("FULL"))
e = BizHawk(log_name="l9heli_fix_diag.log"); e.load(BM); t = e.byte(0x0B); k = 8279; shown = 0; lag_at = []
def ex(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x448], m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x51A]) + ((m[0x466], m[0x3D0]) if FULL else ())
def lstep(b):
    global t
    for _ in range(8):
        e.step(bt(b), 1); m = e.ram(0, 0x800)
        if m[0x0B] != t: break
        lag_at.append(k + 1)
    t = m[0x0B]; return m
while k < STOP:
    ed = [x for x in EDITS if x["A"] == k]
    if ed:
        n0 = len(lag_at)
        for i, b in enumerate(ed[0]["inputs"]): m = lstep(b)
        k = ed[0]["TGT"]; ref = bytes(R[OFF + k - 1])
        print(f"edit {ed[0]['A']}->{k}: lag frames inside {len(lag_at) - n0}; ours {ex(m)} old {ex(ref)} | {ostr(m)}", flush=True); continue
    m = lstep(ins[OFF + k]); k += 1; ref = bytes(R[OFF + k - 1])
    if ex(m) != ex(ref) and shown < SHOW:
        shown += 1; print(k, repr(ins[OFF + k - 1]), "ours", ex(m), "old", ex(ref), "|", ostr(m), "| old", ostr(ref), flush=True)
print("lag frames at", lag_at, flush=True)
e.close()
