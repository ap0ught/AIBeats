"""Is "fresh launch" the same as "reset()"? Plays the same movie both ways and compares RAM and the trace.

    python tools/launch_vs_reset.py <inputs (bk2 numbering, row 1 empty)> [frames]

Launch: the bridge connects at framecount 1 (frame 1 already emulated, no input) -> play rows[1:].
Reset:  reset() -> framecount 0 -> play rows. Both end at the same framecount; RAM SHA-1 and the per-frame
trace (frame number + all fields) must be identical.
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402

if __name__ == "__main__":
    rows = read_inputs(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else len(rows)
    rows = rows[:n]
    assert rows[0] == (), "row 1 must be empty"
    res = {}
    for how in ("launch", "reset"):
        e = BizHawk(log_name=f"lvr_{how}.log")
        try:
            print(how, "connected at framecount", e.state().frame)
            e.trace(True)
            if how == "reset":
                print("  after reset framecount", e.reset().frame)
                e.run(rows)
            else:
                e.run(rows[1:])
            tr = [s for s in e.last_trace]
            res[how] = (hashlib.sha1(e.ram_all()).hexdigest(), {s.frame: str(s) for s in tr}, e.state().frame)
        finally:
            e.close()
    a, b = res["launch"], res["reset"]
    common = sorted(set(a[1]) & set(b[1]))
    diff = [f for f in common if a[1][f] != b[1][f]]
    print("end framecount", a[2], b[2], "RAM sha1", a[0][:12], b[0][:12], "SAME" if a[0] == b[0] else "DIFFERENT")
    print("frames compared", len(common), "differing", len(diff), diff[:10])
