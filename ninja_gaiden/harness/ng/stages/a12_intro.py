"""Power-on -> 1-1 control with the human intro; compare RAM with the TAS's control state."""
import sys, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.emulator import BizHawk
from ng.inputs import read_inputs
from ng.mode import TICKS

if __name__ == "__main__":
    rows = read_inputs("logs/intro_human.inputs.txt")[:173] + [("Right",)]
    with BizHawk(log_name="a12_intro.log") as e:
        e.reset(); e.tick(TICKS)
        s = e.run(rows)
        a = e.ram_all()
        e.save("a12_intro_174")
        print("intro end", s)
        e.load("ref4751/00_1-1_control")
        b = e.ram_all()
        d = [i for i in range(2048) if a[i] != b[i]]
        print("RAM differs at", [hex(i) for i in d][:40], len(d))
