"""Mesen: play rows (already legal) from a .mst; print Ryu every k rows in [a, b).
    python work/c5/mwatch.py <mst> <rows> a b k"""
import sys
sys.path.insert(0, '.')
from ng import fastcore as F
from ng.solve import common as C
mst, rf, a, b, k = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
rows = C.rows_of(rf)
with F.FastCore(boot_rows=None, ticks=False) as fc:
    fc.load_file(mst, 's')
    for i, r in enumerate(rows[:b]):
        fc.step([r])
        if i >= a and (i - a) % k == 0:
            m = fc.ram()
            ax = ((m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51] + m[0x86])
            print(i, "+".join(r) or "-", f"room {m[0x6E]} X {ax} x {m[0x86]} y {m[0x8A]} f{m[0x84]:02x} an{m[0x80]} hp {m[0x65]} np {m[0x64]} it {m[0xC9]}",
                  " ".join(f"{m[0x400+j]:02x}:{m[0x460+j]},{m[0x480+j]}" for j in range(8) if m[0x400+j]))
