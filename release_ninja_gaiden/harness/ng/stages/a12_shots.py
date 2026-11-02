"""Screenshots of the TAS at given frames: python a12_shots.py <state> f1 f2 ..."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng import legal
from ng.emulator import BizHawk

if __name__ == "__main__":
    ref = legal.TasRef()
    with BizHawk(log_name="a12_shots.log") as e:
        s = e.load(sys.argv[1])
        cur = s["frame"]
        for f in map(int, sys.argv[2:]):
            e.run(ref.rows[cur:f]); cur = f
            e.screenshot(f"a12/tas_{f}")
