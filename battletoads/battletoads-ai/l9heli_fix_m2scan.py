"""Second corridor mine: scan a longer/shorter stand before the dash jump (old idle frames 8724-8735).  For w in -8..+24 replace the old idle
input 8730 by 1+w idle frames (w < 0: drop -w idle inputs), replay (with the earlier repairs) and report where the toad's track first leaves
the old run's and the first health loss."""
import json, sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
BM = sys.argv[1]; EDITS0 = json.load(open(sys.argv[2]))
e = BizHawk(log_name="l9heli_fix_m2scan.log")
def okin(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10])
e.load(BM); t = e.byte(0x0B)
def lstep(b):
    global t
    for _ in range(8):
        e.step(bt(b), 1); m = e.ram(0, 0x800)
        if m[0x0B] != t: break
    t = m[0x0B]; return m
k = 8279
while k < 8720:
    ed = [x for x in EDITS0 if x["A"] == k]
    if ed:
        for b in ed[0]["inputs"]: e.step(bt(b), 1)
        k = ed[0]["TGT"]; t = e.byte(0x0B); continue
    m = lstep(ins[OFF + k]); k += 1
print("at 8720 equal to old:", okin(m) == okin(bytes(R[OFF + 8720 - 1])), flush=True)
base = e.msave(); t_base = t
for w in range(-8, 41):
    e.mload(base); t = t_base; k = 8720; first = None; hpd = None; shd = None
    while k < 9000:
        if k == 8729:
            if w >= 0:
                for _ in range(1 + w): m = lstep("")
                k = 8730
            else:
                k = 8730 - w                                   # drop -w idle inputs (8730..8730-w-1 are idle)
                m = lstep("")
            continue
        m = lstep(ins[OFF + k]); k += 1; ref = bytes(R[OFF + k - 1])
        if okin(m) != okin(ref):
            if first is None: first = (k, okin(m), okin(ref))
            if hpd is None and okin(m)[3] != okin(ref)[3]: hpd = (k, okin(m), okin(ref)); break
        if k == 8785: shd = (m[0x466], ref[0x466])
    print(f"w {w:+d}: first track diff {first} hp diff {hpd} $466 at 8785 (ours, old) {shd}", flush=True)
e.close()
