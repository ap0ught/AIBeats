"""From L4_tas_16770 (in sync with TAS #5093 up to its first banned frame), find the earliest legal pickup of the ice
block (0x38): hold A1 for n1 frames, nothing for n2, then B; pickup = toad anim $3B5 reaches 13 (carrying)."""
from toads.emulator import BizHawk

def main():
    e = BizHawk(log_name="l4pick.log")
    e.load("L4_tas_16770")
    root = e.msave()
    best = []
    for a1 in ((), ("Right",), ("Left",)):
        for n1 in range(0, 22, 2):
            for n2 in range(0, 60):
                e.mload(root)
                for _ in range(n1): e.step(a1, 1)
                for _ in range(n2): e.step((), 1)
                e.step(("B",), 1)
                got = None
                for k in range(12):
                    m = e.ram(0, 0x800)
                    if m[0x3B5] == 13: got = n1 + n2 + 1 + k; break
                    e.step((), 1)
                if got is not None:
                    m = e.ram(0, 0x800)
                    best.append((got, a1, n1, n2, m[0x3FD] | m[0x3EE] << 8, m[0x439]))
                    break          # larger n2 only later
    best.sort()
    for b in best[:12]: print(b)
    e.close()

if __name__ == "__main__":
    main()
