"""NesHawk: replay power-on rows (file1 + file2 ...) from reset and save states/<name>.State; print RAM summary.
    python work/c5/nhstate.py <name> <rows file> [<rows file> ...]"""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
name = sys.argv[1]
rows = []
for f in sys.argv[2:]:
    rows += C.rows_of(f)
e = C.open_emu(f"c5_nhstate_emu.log")
try:
    e.reset()
    e.tick(TICKS)
    st = e.run(rows)
    e.save(name)
    m = e.ram_all()
    print(name, "frame", st["frame"], "rows", len(rows), "stage", m[0x6D], "room", m[0x6E], "x", m[0x86], "y", m[0x8A], "hp", m[0x65], "np", m[0x64], "it", m[0xC9])
finally:
    e.close()
