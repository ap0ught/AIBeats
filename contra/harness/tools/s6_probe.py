"""Probe: speed of traced stepping, and a first look at stage 6 from the debug state (hold Right, no fire)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s6lib import Sim, FIELDS, LEAN  # noqa: E402

stage = int(sys.argv[1]) if len(sys.argv) > 1 else 6
with Sim(f"s{stage}_probe") as sim:
    f0 = sim.load(f"dbg/s{stage}_pre")
    print("pre:", {k: f0[k] for k in ("frame", "fc", "rng", "lroutine", "level", "weapon", "x", "y", "lives")})
    t = time.time()
    tr = sim.run([("Right",)] * 600)
    dt = time.time() - t
    print(f"600 frames chunked, rich trace: {600 / dt:.0f} fps")
    for f in tr[:70:3]:
        print(f["frame"], "fc", f["fc"], "lr", f["lroutine"], "x", f["x"], "y", f["y"], "pst", f["pstate"], "jump", f["jump"],
              "fall", f["fall"], "inv", f["inv"], "cam", f.cam, "lag", f["lagged"])
    dead = next((f for f in tr if f.dead), None)
    print("death:", dead and (dead["frame"], dead.wx, dead["y"]))
    sim.load(f"dbg/s{stage}_pre")
    t = time.time()
    for i in range(300):
        sim.run([("Right",)])
    dt = time.time() - t
    print(f"300 frames one by one, rich trace: {300 / dt:.0f} fps")
    sim.set_fields(LEAN)
    sim.load(f"dbg/s{stage}_pre")
    t = time.time()
    tr = sim.run([("Right",)] * 600)
    dt = time.time() - t
    print(f"600 frames chunked, lean trace: {600 / dt:.0f} fps")
    t = time.time()
    for i in range(50):
        sid = sim.msave()
        sim.mload(sid)
        sim.mfree(sid)
    print(f"msave+mload+mfree: {(time.time() - t) / 50 * 1000:.1f} ms")
