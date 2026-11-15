"""Play an input file in BizHawk from power-on and keep the 2 KB of RAM after every frame.

    python work/bizhawk_trace.py logs/cal1.inputs.txt [more.inputs.txt ...]
        -> logs/cal1.ram.npy   uint8 [frames + 1, 2048]; row 0 = RAM at power-on (before any frame)
           logs/cal1.lag.npy   uint8 [frames]; 1 = BizHawk lag frame (the game did not read the controller)

One emulator, started on the hidden desktop, closed when done (our own process only). Refuses to start when
memory is short (the machine is shared with the TMNT session).
"""
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tet.emulator import BizHawk, free_memory_mb
from tet.inputs import read_inputs


def main():
    files = [Path(a) for a in sys.argv[1:]]
    print("memory before launch (available MB, commit headroom MB):", free_memory_mb(), flush=True)
    t0 = time.time()
    with BizHawk(fields={}) as emu:
        print("connected in %.1f s; %s" % (time.time() - t0, {k: emu.info[k] for k in ("sys", "board", "romhash", "framecount")}),
              flush=True)
        for p in files:
            rows = read_inputs(p)
            st = emu.reset()
            ram0 = emu.ram_all()
            t1 = time.time()
            states, rams = emu.run_ram(rows)
            dt = time.time() - t1
            arr = np.frombuffer(b"".join([ram0] + rams), dtype=np.uint8).reshape(len(rows) + 1, 2048)
            lag = np.array([s.lagged for s in states], dtype=np.uint8)
            out = p.with_name(p.name.replace(".inputs.txt", ".ram.npy"))
            np.save(out, arr)
            np.save(p.with_name(p.name.replace(".inputs.txt", ".lag.npy")), lag)
            print(f"{p.name}: {len(rows)} frames in {dt:.1f} s ({len(rows) / dt:.0f} fps); first frame number "
                  f"{states[0].frame}, last {states[-1].frame}; lag frames {int(lag.sum())}; -> {out.name}", flush=True)
    print("emulator closed; memory now:", free_memory_mb())


if __name__ == "__main__":
    main()
