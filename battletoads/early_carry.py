"""EARLY track (2026-10-09): WHAT carries over a level load?  Diff the whole 2 KB of RAM between two entry bookmarks of
the same level that were reached behind DIFFERENT upstream routes, at the bookmark and after n idle frames.

    python early_carry.py A B [A2 B2 ...]     -> prints the differing addresses; logs/fix/early_carry.txt
"""
import sys

from toads.emulator import BizHawk, LOGS_DIR

out = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


def main(pairs):
    e = BizHawk(log_name="early_carry.log")
    for a, b in pairs:
        rams = {}
        for name in (a, b):
            e.load(name)
            e.step((), 1)                     # load applies on the next step
            seq = [e.ram_all()]
            for n in range(60):
                e.step((), 1)
                seq.append(e.ram_all())
            rams[name] = seq
        say(f"=== {a} vs {b}")
        for n in (0, 1, 2, 5, 10, 20, 40, 60):
            ra, rb = rams[a][n], rams[b][n]
            d = [i for i in range(0x800) if ra[i] != rb[i]]
            say(f" +{n:2d} idle: {len(d)} bytes differ:", " ".join(f"${i:03x}:{ra[i]:02x}/{rb[i]:02x}" for i in d[:60]))
    e.close()
    open(LOGS_DIR / "fix" / "early_carry.txt", "a", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(list(zip(a[0::2], a[1::2])))
