import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.emulator import BizHawk
from ng.inputs import read_inputs
from ng.mode import TICKS

if __name__ == "__main__":
    rows = read_inputs("logs/tas4751.inputs.txt")
    with BizHawk(log_name="a12_probe1.log") as e:
        for nm in []:
            s = e.load("ref4751/" + nm)
            print(nm, "frame", s.frame, "stage", s.stage, "room", s.room, "x", s.x, "y", s.y, "timer", s.timer, s.subtimer)
        s = e.load("ref4751/00_1-1_control")
        f0 = s.frame
        e.trace(True)
        t = time.time()
        e.run(rows[f0:f0 + 600])     # row index f0 (0-based) = frame f0+1
        tr1 = e.last_trace
        print("fps", 600 / (time.time() - t))
        e.load("ref4751/00_1-1_control")
        strip = [tuple(b for b in r if not ("Up" in r and "Down" in r and b in ("Up", "Down"))) for r in rows[f0:f0 + 600]]
        e.run(strip)
        tr2 = e.last_trace
        keys = ["x","xsub","y","scroll","scroll_scr","room","stage","hp","vx","vy"]
        for i, (a, b) in enumerate(zip(tr1, tr2)):
            d = [k for k in keys if a[k] != b[k]]
            if d:
                print("first diff at frame", a.frame, d, [(a[k], b[k]) for k in d]); break
        else:
            print("no diff in 600 frames")
