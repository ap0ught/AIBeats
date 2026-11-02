"""Round 5: build a Mesen state (states/mesen/r5/<out>.mst + .frame) by power-on replay of a spec.
    python work/r5/mboot.py <out> <item> [<item> ...]
items: tas:<F>        the TAS's NesHawk pad bytes for frames 1..F (exact NesHawk state at TAS frame F)
       rows:<file>    rows of an inputs file (logs/r4/<name> or a path), fed as plain masks
       rows:<file>:<n> only the first n rows
       blank:<n>      n empty rows
Prints the final frame and Ryu's room/x/y/hp."""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P))
from ng import fastcore as F  # noqa
from ng.inputs import read_inputs, to_mask  # noqa


def rows_file(n):
    for c in (n, f"logs/r4/{n}.inputs.txt", f"logs/r5/{n}.inputs.txt", f"logs/{n}.inputs.txt", f"logs/a34/{n}.inputs.txt"):
        if (P / c).exists():
            return P / c
    raise FileNotFoundError(n)


def build(items):
    b = bytearray()
    for it in items:
        k, v = it.split(":", 1)
        if k == "tas":
            b += F.neshawk_pads(P / "logs/tas4751.trace.csv", int(v))
        elif k == "rows":
            parts = v.rsplit(":", 1)
            n = None
            if len(parts) == 2 and parts[1].isdigit():
                v, n = parts[0], int(parts[1])
            rr = read_inputs(rows_file(v))
            if n is not None:
                rr = rr[:n]
            b += bytes(to_mask(r) for r in rr)
        elif k == "blank":
            b += bytes(int(v))
    return bytes(b)


if __name__ == "__main__":
    out = sys.argv[1]
    boot = build(sys.argv[2:])
    with F.FastCore(boot_rows=boot) as fc:
        fc.save("b")
        p = fc.save_file("b", P / "states/mesen/r5" / f"{out}.mst", len(boot))
        r = fc.ram()
        print("wrote", p, "frame", len(boot), "stage", r[0x6D], "room", r[0x6E], "x", r[0x86], "y", r[0x8A], "hp", r[0x65],
              "scroll", r[0x52], r[0x51])
