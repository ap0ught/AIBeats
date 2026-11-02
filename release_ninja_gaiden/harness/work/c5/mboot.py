"""Boot Mesen from a power-on history with NesHawk's pads, save states/mesen/<name>.mst, print key RAM.
    python work/c5/mboot.py <history inputs> <trace csv> <frame> <name>"""
import sys, time
sys.path.insert(0, '.')
from ng import fastcore as F
from ng.inputs import read_inputs
h, tr, n, name = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
pads = F.neshawk_pads(tr, n)
t = time.time()
with F.FastCore(boot_rows=pads, ticks=False) as fc:
    fc.save("b")
    fc.save_file("b", F.STATES / f"{name}.mst", n)
    r = fc.ram()
print(f"booted {n} in {time.time()-t:.0f}s")
print("x", r[0x86], "y", r[0x8A], "hp", r[0x65], "np", r[0x64], "stage", r[0x6D], "room", r[0x6E], "bf", r[0xBF], "62", r[0x62])
print("slots", " ".join(f"{r[0x400+i]:02x}:{r[0x460+i]},{r[0x480+i]}" for i in range(8)))
