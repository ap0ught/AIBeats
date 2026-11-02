"""Smoke test: launch NesHawk, identify core/ROM, step, screenshot, RAM/OAM read, speed, quit.

    python tools/smoke.py
"""
import hashlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk  # noqa: E402

if __name__ == "__main__":
    t0 = time.time()
    e = BizHawk(log_name="smoke.log", fields={})
    try:
        print("pid", e.pid, "boot", round(time.time() - t0, 1), "s")
        print({k: v for k, v in e.info.items() if k != "domains"}, e.info["domains"])
        print("first state", e.state())
        t0 = time.time()
        s = e.step((), 600)
        print("600 frames:", s, f"{600 / (time.time() - t0):.0f} fps")
        e.screenshot("smoke_f600")
        print("ram sha1", hashlib.sha1(e.ram_all()).hexdigest())
        print("oam", e.oam()[:16].hex())
        t0 = time.time()
        s = e.run([()] * 3000)
        print("3000 frames via run():", s, f"{3000 / (time.time() - t0):.0f} fps")
        print("reset ->", e.reset())
    finally:
        e.close()
