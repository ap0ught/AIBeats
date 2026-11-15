"""Compare the ROM-level model with a BizHawk RAM trace, frame by frame, over all 2048 bytes of RAM.

    python work/compare_trace.py cal1 [cal2 ...] [--shift K] [--max 20] [--ignore 0x100-0x1FF]

--shift K : compare model frame f with BizHawk frame f + K (to find a constant frame offset)
Prints the first frames that differ and the addresses involved; exit code 0 only if every frame matches.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tet.inputs import read_inputs, to_mask
from tet.nes import Machine

LOGS = Path(__file__).resolve().parent.parent / "logs"


def compare(name, shift=0, max_report=12, ignore=(), verbose=True, machine=None):
    rows = read_inputs(LOGS / f"{name}.inputs.txt")
    ref = np.load(LOGS / f"{name}.ram.npy")
    masks = [to_mask(r) for r in rows]
    m = machine or Machine()
    keep = np.ones(2048, dtype=bool)
    for lo, hi in ignore:
        keep[lo:hi + 1] = False
    bad = 0
    first_bad = None
    n = len(masks)
    if verbose:
        d0 = np.nonzero((np.frombuffer(bytes(m.ram), dtype=np.uint8) != ref[0]) & keep)[0]
        print(f"{name}: power-on RAM differs at {len(d0)} addresses" + (f", e.g. {[hex(a) for a in d0[:8]]}" if len(d0) else ""))
    for f in range(1, n + 1):
        m.frame(masks[f - 1])
        g = f + shift
        if g < 1 or g > n:
            continue
        mine = np.frombuffer(bytes(m.ram), dtype=np.uint8)
        diff = np.nonzero((mine != ref[g]) & keep)[0]
        if len(diff):
            bad += 1
            if first_bad is None:
                first_bad = f
            if verbose and bad <= max_report:
                print(f"  frame {f}: {len(diff)} bytes differ: " +
                      ", ".join(f"${a:03X} sim={mine[a]:02X} biz={ref[g][a]:02X}" for a in diff[:10]) +
                      (" ..." if len(diff) > 10 else ""))
    if verbose:
        print(f"{name}: {n} frames, {bad} differ" + (f" (first at {first_bad})" if bad else " -> IDENTICAL"))
    return bad, first_bad


def main():
    args = sys.argv[1:]
    shift, mx, ignore = 0, 12, []
    if "--shift" in args:
        i = args.index("--shift"); shift = int(args[i + 1]); del args[i:i + 2]
    if "--max" in args:
        i = args.index("--max"); mx = int(args[i + 1]); del args[i:i + 2]
    while "--ignore" in args:
        i = args.index("--ignore")
        lo, hi = args[i + 1].split("-")
        ignore.append((int(lo, 0), int(hi, 0)))
        del args[i:i + 2]
    total = 0
    for name in args:
        total += compare(name, shift, mx, ignore)[0]
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
