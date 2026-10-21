"""How fast can NesHawk go? Tries frameskip and invisible emulation via ad-hoc bridge commands."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402

core = sys.argv[1] if len(sys.argv) > 1 else "NesHawk"
with BizHawk(log_name="speedtest.log", fields={}, core=core) as e:
    def t(label, n=1500):
        t0 = time.time()
        e.run([()] * n)
        print(f"{label}: {n / (time.time() - t0):.0f} fps", flush=True)
    t("default fast")
    e.frameskip(9)
    t("frameskip 9")
    for c in ("invis on", "speed 6400"):
        try:
            print(c, e.cmd(c))
            t(c)
        except Exception as ex:
            print(c, "failed:", ex)
