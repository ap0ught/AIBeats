"""print boss / Ryu / slots per row for a wanted plan from the 3-3 state (Mesen)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/c5')
from ng import fastcore as F
from ng.solve import common as C, legality as L
from ng.inputs import to_mask
rows = C.rows_of(sys.argv[1])
a, b, every = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 1
legalize = '--raw' not in sys.argv
hist = C.rows_of('logs/tk_to33.inputs.txt')
if legalize:
    en = L.Enforcer(hist[-1900:])
    rows = [en.emit(w) for w in rows]
with F.FastCore(boot_rows=None, ticks=False) as fc:
    fc.load_file('states/mesen/c5_33c.mst', 's')
    for i, r in enumerate(rows[:b]):
        fc.step([r])
        m = fc.ram()
        if i >= a and (i - a) % every == 0:
            print(i, "+".join(r) or "-", f"ryu x{m[0x86]} y{m[0x8A]} f{m[0x84]:02x} an{m[0x80]} hp{m[0x65]} np{m[0x64]} inv{m[0x95]}",
                  f"boss x{m[0x467]} y{m[0x487]} hp{m[0x497]}", " ".join(f"{m[0x400+j]:02x}:{m[0x460+j]},{m[0x480+j]}" for j in range(7)))
