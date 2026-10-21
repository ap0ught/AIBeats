"""probe: core-state differences N frames into Level 9 behind different Level 8 ends (reference: L8c_end0)
    python u16a_p3.py N bookmark [bookmark ...]"""
import sys
from u16a_lib import *
import u16a_hid as H
N = int(sys.argv[1]); nxt = seg("L9heli_c2")
e = BizHawk(log_name="u16a_p3.log")
res = {}
for bm in ["L8c_end0"] + sys.argv[2:]:
    e.load(bm)
    for b in nxt[:N]: e.step(bt(b), 1)
    ram = bytes(e.ram(0, 0x800))
    blob, bl = H.core(e, "p3")
    e.step((), 1)
    res[bm] = (ram, blob, bl)
r0 = res["L8c_end0"]
print("blob", len(r0[1]), "head", r0[1][:16].hex(), "blocks", [(k, len(v)) for k, v in r0[2].items()])
for bm in sys.argv[2:]:
    ram, blob, bl = res[bm]
    print(f"== {bm} vs L8c_end0 at L9 frame {N}: RAM differs {[hex(a) for a in range(0x800) if ram[a] != r0[0][a] and not 0x100 <= a < 0x200][:12]}; blob bytes differing {sum(1 for x, y in zip(blob, r0[1]) if x != y)}")
    for tag in bl:
        x, y = bl[tag], r0[2].get(tag, b"")
        d = [i for i in range(min(len(x), len(y))) if x[i] != y[i]]
        if d: print(f"   block {tag} len {len(x)}: {len(d)} differ " + " ".join(f"+{i}:{y[i]:02x}/{x[i]:02x}" for i in d[:30]))
e.close()
