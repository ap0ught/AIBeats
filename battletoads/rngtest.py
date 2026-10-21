"""Which parts of the old later-level segments depend on the random numbers? (debug tool, snapshots only)
Load a segment's root bookmark, optionally POKE the RNG bytes $25-$28 to other values, replay the segment's inputs
and compare the toad's track with the unpoked replay: the first divergence shows where a re-search is needed on a
new upstream route.

    python rngtest.py L9a L10a ...
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR


def track(e, d, rng=None):
    e.load(d["bookmark"])
    e.step((), 0) if False else None
    if rng:
        for i, v in enumerate(rng):
            e.poke(0x25 + i, v)
    out = []
    for b in d["inputs"]:
        e.step(tuple(v for v in b.replace("+", ",").split(",") if v), 1)
        m = e.ram(0, 0x800)
        out.append((m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x51A], m[0x11], m[0x10]))
    return out


def main(names):
    e = BizHawk(log_name="rngtest.log")
    for name in names:
        d = json.load(open(LOGS_DIR / f"pbeam_{name}.json"))
        base = track(e, d)
        print(name, "bookmark", d["bookmark"], len(d["inputs"]), "frames; base end", base[-1], flush=True)
        for rng in ((0x12, 0x34, 0x56, 0x78), (0xA5, 0x5A, 0x3C, 0xC3), (0x01, 0x80, 0xFE, 0x7F)):
            t = track(e, d, rng)
            div = next((i for i, (a, b) in enumerate(zip(base, t)) if a != b), None)
            print("   rng", bytes(rng).hex(), "first divergence at", div, "| end", t[-1], "| lives lost" if t[-1][3] < base[-1][3] else "", flush=True)
    e.close()


if __name__ == "__main__":
    main(sys.argv[1:])
