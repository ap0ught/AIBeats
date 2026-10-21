"""Final builder probe: two input lists from power-on, the toad compared frame by frame (is a level free of the dice?).
    python u17f_cmp.py <tag> <shift> <segments A (comma separated)> <segments B (comma separated)>
        route B's frame n + shift is compared with route A's frame n (shift = len(B) - len(A) when a page was shortened)
        compared: toad key (x, height, depth, z, health, level byte, lives), score; listed: where the dice $25-$28 first differ
    -> logs/fix/u17f_cmp_<tag>.txt.   No memory writes."""
import sys

from u17f_lib import *

tag, A, B = sys.argv[1], sys.argv[3].split(","), sys.argv[4].split(",")
shift = 0 if sys.argv[2] == "auto" else int(sys.argv[2])
log = Log(f"u17f_cmp_{tag}.txt")


def run(names):
    ins = route_inputs(names)
    e = BizHawk(log_name=f"u17f_cmp_{tag}.log")
    out = []
    for n, b in enumerate(ins, 1):
        e.step(bt(b), 1)
        if n >= 1900:
            m = e.ram(0, 0x800)
            out.append((key(m), bytes(m[0x5F4:0x5FA]), bytes(m[0x25:0x29]), m[0x0B]))
        else:
            out.append(None)
    m = bytes(e.ram(0, 0x800))
    e.close()
    return out, m


a, ma = run(A)
b, mb = run(B)
if sys.argv[2] == "auto":                                     # align the two runs on the frame the level byte LAST changes before the end of each
    def last_change(r):
        lv = [x[0][5] if x else None for x in r]
        return max(i for i in range(1901, len(lv)) if lv[i] != lv[i - 1])
    shift = last_change(b) - last_change(a)
log(f"A = intro + {' '.join(A)}: {len(a)} inputs; end {toad(ma)}")
log(f"B = intro + {' '.join(B)}: {len(b)} inputs; end {toad(mb)}")
nk = nd = 0
fk = fd = None
lk = None
for n in range(1900, min(len(a), len(b) - shift)):
    x, y = a[n], b[n + shift]
    if x is None or y is None:
        continue
    if x[0] != y[0] or x[1] != y[1]:
        nk += 1
        lk = n + 1
        if fk is None:
            fk = n + 1
    if x[2] != y[2]:
        nd += 1
        if fd is None:
            fd = n + 1
d = diff(ma, mb)
log(f"compared A frame n with B frame n{shift:+d}: toad key / score differ on {nk} frames (first {fk}, last {lk}); dice differ on {nd} frames (first {fd}); "
    f"end RAM differs in {len(d)} bytes {[hex(i) for i in d[:40]]}")
