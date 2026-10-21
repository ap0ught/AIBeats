"""Day-1 smoke test: launch, identify the core, step, screenshot, read RAM/OAM, quit.

    python tools/smoke.py [NesHawk|quickerNES]
"""
import hashlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402

core = sys.argv[1] if len(sys.argv) > 1 else None
t0 = time.time()
e = BizHawk(log_name=f"smoke_{core or 'default'}.log", fields={}, core=core)
try:
    print("pid", e.pid, "boot", round(time.time() - t0, 1), "s")
    print({k: v for k, v in e.info.items()})
    t0 = time.time()
    s = e.step((), 600)
    print("600 frames:", s, f"{600 / (time.time() - t0):.0f} fps")
    e.screenshot(f"smoke_{e.core}_f600")
    ram = e.ram_all()
    print("ram sha1", hashlib.sha1(ram).hexdigest())
    try:
        print("oam", e.oam()[:16].hex())
    except Exception as ex:
        print("oam failed:", ex)
    t0 = time.time()
    s = e.run([()] * 3000)
    print("3000 frames via run():", s, f"{3000 / (time.time() - t0):.0f} fps")
finally:
    e.close()
