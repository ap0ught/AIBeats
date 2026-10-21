"""Job (worker): replay stage 6 + stage 7 as ONE input list from the stage 6 start state, twice, and check that
the frame after the last row is stage 8's first playable frame, with no death and weapon $13.
Environment S7_CHAIN = "s6 state|s6 run|s7 run;..." """
import hashlib
import os
from pathlib import Path
from contra.inputs import read_inputs

ROOT = Path(r"")
for item in os.environ.get("S7_CHAIN", "s6/ph66|final_ph66|f_chain66").split(";"):
    st, a, b = item.split("|")
    r6 = read_inputs(ROOT / "logs" / "s6" / f"{a}.inputs.txt")
    r7 = read_inputs(ROOT / "logs" / "s7" / f"{b}.inputs.txt")
    rows = r6 + r7
    hs = []
    for k in range(2):
        f0 = sim.load(st)
        h = hashlib.sha1()
        died = False
        lag = 0
        first7 = None
        for i in range(0, len(rows), 1000):
            for j, f in enumerate(sim.run(rows[i:i + 1000])):
                h.update(bytes([f["x"], f["y"], f["screen"], f["scroll"], f["rng"], f["fc"], f["lroutine"], f["level"],
                                f["death"] & 1, f["weapon"], f["lagged"]]))
                died = died or f.dead
                lag += f["lagged"]
                if first7 is None and f["level"] == 6 and f["lroutine"] == 4:
                    first7 = i + j
        last = f
        nxt = sim.run([()])[-1]
        hs.append(h.hexdigest())
    print(st, a, "+", b, "rows", len(r6), "+", len(r7), "=", len(rows), "| stage 7's first playable frame at row", first7,
          "| replays identical:", hs[0] == hs[1], "| died:", died, "| lag", lag, "| last row: level", last["level"],
          "lroutine", last["lroutine"], "| next frame: level", nxt["level"], "lroutine", nxt["lroutine"], "weapon",
          hex(nxt["weapon"]), "fc", nxt["fc"], flush=True)
