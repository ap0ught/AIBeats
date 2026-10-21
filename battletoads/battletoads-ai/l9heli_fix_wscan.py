"""For a join bookmark + the mine-1 repair: try several waits w before the dash jump over corridor mine 2 (old idle input 8730 replaced by
1+w idle frames) and replay the old inputs lag-aware to the Level 10 entry and NA frames beyond.  Reports per w: first health/level
difference, raw frames lost after T', whether the Level 10 entry RAM equals the old run's and how many of the next NA frames do.
    python l9heli_fix_wscan.py <bookmark> <edits json (mine 1)> <w list a,b,c> [select old indices a/b or -]"""
import json, sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
BM = sys.argv[1]; EDITS0 = json.load(open(sys.argv[2])); WS = [int(v) for v in sys.argv[3].split(",")]
SEL = set(int(v) for v in sys.argv[4].split("/") if v not in ("", "-")) if len(sys.argv) > 4 else set()
NA = 30; VOL = set(range(0x100, 0x200))
e = BizHawk(log_name="l9heli_fix_wscan.log")
def trk(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10])
e.load(BM); t = e.byte(0x0B); raw = 0
def lstep(b):
    global t, raw
    for _ in range(8):
        e.step(bt(b), 1); raw += 1; m = e.ram(0, 0x800)
        if m[0x0B] != t: break
    t = m[0x0B]; return m
k = 8279
while k < 8720:
    ed = [x for x in EDITS0 if x["A"] == k]
    if ed:
        for b in ed[0]["inputs"]: m = lstep(b)
        k = ed[0]["TGT"]; continue
    m = lstep(ins[OFF + k]); k += 1
print("at 8720 equal to old:", trk(m) == trk(bytes(R[OFF + 8720 - 1])), "raw", raw, flush=True)
base = e.msave(); t_base = t; raw_base = raw
for w in WS:
    e.mload(base); t = t_base; raw = raw_base; k = 8720; first = None; hpd = None; end = None
    while k < 9987:
        if k == 8729:
            for _ in range(1 + w): m = lstep("")
            k = 8730; continue
        b = ins[OFF + k]
        if (k + 1) in SEL: b = (b + ",Select").lstrip(",")
        if k >= 9650:
            e.step(bt(b), 1); raw += 1; m = e.ram(0, 0x800); t = m[0x0B]
        else: m = lstep(b)
        k += 1; ref = bytes(R[OFF + k - 1])
        if end is None and m[0x10] != 11: end = k
        if trk(m) != trk(ref):
            if first is None: first = (k, trk(m), trk(ref))
            if hpd is None and trk(m)[3:] != trk(ref)[3:]: hpd = (k, trk(m), trk(ref)); 
            if hpd and k < 9900: break
    eq0 = None; same = 0
    if k == 9987:
        ref = bytes(R[OFF + 9987 - 1]); eq0 = not [a for a in range(0x800) if m[a] != ref[a] and a not in VOL]
        for j in range(NA):
            F = OFF + 9987 + j
            e.step(bt(ins[F]), 1); m = e.ram(0, 0x800); ref = bytes(R[F])
            if not [a for a in range(0x800) if m[a] != ref[a] and a not in VOL]: same += 1
    print(f"w {w:+d}: lost after T' {raw - (k - 8279)} frames; first track diff {first}; hp/level diff {hpd}; level end at old {end}; entry RAM equal {eq0}; next {NA} frames equal: {same}", flush=True)
e.close()
