"""Explore power-on -> title -> Start -> first cutscene, RAM every frame, screenshots every 60 frames."""
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, LOGS_DIR

if __name__ == "__main__":
    e = BizHawk(log_name="explore1.log", fields={})
    try:
        rams, sts = [], []
        def go(rows, tag):
            for i in range(0, len(rows), 60):
                s, r = e.run_ram(rows[i:i+60])
                sts.extend(s); rams.extend(r)
                e.screenshot(f"ex1/{tag}_{s[-1]['frame']:05d}")
        go([()] * 700, "a")
        e.save("ex1_title700")
        go([("Start",)] * 2 + [()] * 1200, "b")
        e.save("ex1_after_start")
        np.save(LOGS_DIR / "ex1.ram.npy", np.frombuffer(b"".join(rams), dtype=np.uint8).reshape(-1, 2048))
        with open(LOGS_DIR / "ex1.states.txt", "w") as f:
            for s in sts: f.write(str(s) + "\n")
    finally:
        e.close()
