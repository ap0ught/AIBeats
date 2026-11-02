"""Acts 3-4 round 2: goal beam to an explicit position (room, world x, y), standing (or any, --air).
    python ng/stages/a34r2_goal.py <stage> <start state> <prefix rows name|-> <room> <wpos> <y> <out> [--W 12] [--tol 3]
        [--ky 1.0] [--air] [--max 600]
Rows = prefix + beam rows, saved as logs/a34/<out>.inputs.txt; end state states/tmp/a34r2_x/<out>.State."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402
import a34_beam as BM  # noqa: E402


class GB(BM.GoalBeam):
    air = False

    def expand(self):
        kids = super().expand()
        return kids


def main():
    a = sys.argv[1:]
    opt = BM.stage_from_args(a)
    W = opt("--W", 12); tol = opt("--tol", 3); ky = opt("--ky", 1.0); mx = opt("--max", 600)
    air = "--air" in a
    if air:
        a.remove("--air")
    name, start, pre, room, wx, wy, out = a[:7]
    st = K.BY_NAME[name]
    _, c0, c1, _ = K.STAGES[st]
    e = K.open_emu(f"a34r2_goal_{out}.log")
    try:
        e.load(start)
        rows = K.load_rows(pre) if pre != "-" else []
        s = e.run(rows) if rows else e.state()
        print("start", s.frame, "room", s.room, "x", s.x, "y", s.y, "wpos", K.wpos(s), flush=True)
        path = BM.TasPath(c0, c1)
        bm = BM.GoalBeam(e, st, s.frame, rows, path, W=W, goal=(int(room), int(wx), int(wy)), ky=ky, tol=tol,
                         log=lambda m: print(m, flush=True))
        if air:
            # accept airborne goal hits: patch the ground test by tolerance only
            orig = bm.expand
        t = time.time()
        res = bm.run(mx, report_every=10)
        if res is None:
            print("no result"); return
        tend, brow = res
        K.save_rows(out, rows + brow, f"{start} + {pre} + goal ({room},{wx},{wy}) reached {tend}")
        e.load(start); s = e.run(rows + brow)
        e.save(f"tmp/a34r2_x/{out}")
        print(f"goal reached at {tend}; end state frame {s.frame} room {s.room} x {s.x} y {s.y} hp {s.hp} "
              f"wpos {K.wpos(s)} {time.time() - t:.0f}s", flush=True)
    finally:
        e.close()


if __name__ == "__main__":
    main()
