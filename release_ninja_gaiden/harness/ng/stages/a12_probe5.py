"""Scan jump timings from a TAS frame: python a12_probe5.py <from_frame> <first_jump> <last_jump> <targetX> <targetY>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng import legal
from ng.emulator import BizHawk
from ng.mode import TICKS

if __name__ == "__main__":
    f0, j0, j1, tx, ty = map(int, sys.argv[1:6])
    second = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    ref = legal.TasRef()
    with BizHawk(log_name="a12_probe5.log") as e:
        s0 = e.load("ref4751/00_1-1_control"); e.tick(TICKS)
        legal.play(e, ref.rows[s0["frame"]:f0])
        sid = e.msave()
        for jf in range(j0, j1 + 1):
            for jf2 in ([0] if not second else range(jf + 5, jf + 40, 2)):
                e.mload(sid)
                rows = []
                for f in range(f0 + 1, f0 + 260):
                    r = {"Right"}
                    if jf <= f < jf + 2 or (jf2 and jf2 <= f < jf2 + 2):
                        r.add("A")
                    rows.append(tuple(r))
                tr = legal.play(e, rows)
                hit = next((s for s in tr if legal.pos_of(s)[2] >= tx and s["y"] <= ty and not (s["rflags"] & 4)), None)
                mx = max(legal.pos_of(s)[2] for s in tr)
                print(jf, jf2, "reach" if hit else "-", hit["frame"] if hit else "", "maxX", mx, "hp", tr[-1]["hp"], "y_end", tr[-1]["y"])
