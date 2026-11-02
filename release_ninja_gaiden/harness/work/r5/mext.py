"""Round 5: extend a Mesen state by rows of a file: python work/r5/mext.py <in.mst> <rows file> <skip> <n> <out name>
plays rows[skip:skip+n] of the file from the state, saves states/mesen/r5/<out>.mst and logs/r5/<out>.inputs.txt =
rows[:skip+n] (the file's rows up to there)."""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P))
from ng import fastcore as F  # noqa
from ng.inputs import read_inputs, write_inputs  # noqa
src, rf, skip, n, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
for c in (rf, f"logs/r5/{rf}.inputs.txt", f"logs/r4/{rf}.inputs.txt"):
    if (P / c).exists():
        rf = P / c
        break
rows = read_inputs(rf)
with F.FastCore() as fc:
    fr = fc.load_file(P / src, "a")
    fc.step(rows[skip:skip + n])
    fc.save("b")
    fc.save_file("b", P / "states/mesen/r5" / f"{out}.mst", fr + n)
    r = fc.ram()
    write_inputs(P / "logs/r5" / f"{out}.inputs.txt", rows[:skip + n], f"{rf.name} rows[:{skip + n}] (frame {fr + n})")
    print("wrote", out, "frame", fr + n, "room", r[0x6E], "x", r[0x86], "y", r[0x8A], "hp", r[0x65])
