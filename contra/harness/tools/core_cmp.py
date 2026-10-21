"""Are NesHawk and quickerNES the same machine for this game? Play one input list on both (quickerNES boots one
frame earlier, so NesHawk gets the list one frame later) and compare a set of RAM bytes frame by frame.

    python tools/core_cmp.py <logs/x.inputs.txt> <movie offset on NesHawk> [frames]
"""
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402
from try_tas import shift  # noqa: E402

F = {"fc": 0x1A, "rng": 0x34, "groutine": 0x18, "lroutine": 0x2C, "level": 0x30, "x": 0x334, "y": 0x31A,
     "screen": 0x64, "scroll": 0x65, "pad": 0xF1, "pstate": 0x90, "death": 0xB4}


def one(path, core, d, n, out):
    rows = shift(read_inputs(path), d)[:n]
    e = BizHawk(log_name=f"corecmp_{core}.log", fields=F, core=core)
    try:
        e.trace(True)
        e.run(rows)
        out[core] = e.last_trace
    finally:
        e.close()


if __name__ == "__main__":
    path, d = sys.argv[1], int(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
    out = {}
    th = [threading.Thread(target=one, args=(path, "NesHawk", d, n, out)),
          threading.Thread(target=one, args=(path, "quickerNES", d - 1, n, out))]
    for t in th:
        t.start()
    for t in th:
        t.join()
    a, b = out["NesHawk"], out["quickerNES"]
    # NesHawk frame f <-> quickerNES frame f-1
    first = {}
    for i in range(1, min(len(a), len(b) + 1)):
        sa, sb = a[i], b[i - 1]
        for k in F:
            if sa[k] != sb[k] and k not in first:
                first[k] = (sa["frame"], sa[k], sb[k])
                print(f"first difference in {k}: NesHawk frame {sa['frame']} = {sa[k]}, quickerNES frame {sb['frame']} = {sb[k]}")
                print("   NesHawk   ", sa)
                print("   quickerNES", sb)
    print("fields never differing:", [k for k in F if k not in first])
    print("lag at end: NesHawk", a[-1]["lag"], "quickerNES", b[-1]["lag"])
    lagA = [s["frame"] for s in a if s["lagged"]]
    lagB = [s["frame"] + 1 for s in b if s["lagged"]]
    print("lag frames NesHawk:", lagA[:40])
    print("lag frames quickerNES (+1):", lagB[:40])
