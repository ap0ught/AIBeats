"""Final builder: replay one segment from a bookmark and save the end state as a bookmark (tool-made, for chain tests).
    python u17f_segend.py <segment>[@bookmark] <bookmark out (Fk... / u17f_...)> [<next level byte>]
prints the end toad, the level-byte changes in the last 100 inputs and whether the toad is set down exactly on the last input."""
import sys
from u17f_lib import *
spec, out = sys.argv[1], sys.argv[2]
LVL = int(sys.argv[3]) if len(sys.argv) > 3 else None
assert out.startswith("Fk") or out.startswith("u17f_")
name, _, bm = spec.partition("@")
sj, sg = segj(name), seg(name)
e = BizHawk(log_name="u17f_segend.log")
e.load(bm or sj["bookmark"])
stage, placed, prev, ch = 0, None, None, []
for i, b in enumerate(sg):
    e.step(bt(b), 1)
    if i >= len(sg) - 100:
        m = e.ram(0, 0x800)
        if m[0x10] != prev:
            ch.append((i + 1, m[0x10]))
        prev = m[0x10]
        if LVL is not None and placed is None:
            stage = placed_stage(stage, m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, LVL)
            if stage == 3:
                placed = i + 1
m = bytes(e.ram(0, 0x800))
e.save(out)
print(f"{name} from {bm or sj['bookmark']}: {len(sg)} inputs; end {toad(m)}; level-byte changes in the last 100 {ch}; set down on input {placed}; saved states/{out}.State")
e.close()
