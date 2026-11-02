"""Round 4: Jaquio model plan (logs/r4/jq_plan_<tag>.json from jqplan.py) -> wanted rows; play them from
tmp/a56r2_64b_control through the a56 Enforcer and compare with the model.
    python work/r4/jqrows.py <plan json> [--save name]"""
import json
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P)); sys.path.insert(0, str(P / "work" / "r4"))
import jqplan as M  # noqa
NI = M.NI
DIR = {1: "Right", -1: "Left"}


def plan_rows(steps, end_extra=6):
    """steps -> list of wanted row sets (index 0 = row 1)."""
    rows = {}

    def add(r, *b):
        rows.setdefault(r, set()).update(b)
    cur_x, cur_t, face = 32.0, 1, 1
    swings = []
    lastslash = -99
    for st in steps:
        if st[0] == "floorwalk":
            _, t0, n = st
            for r in range(t0, t0 + n):
                add(r, "Right")
        elif st[0] == "floorjump":
            _, T, X, F, k = st
            add(T, "A"); add(T + 1, "A")
            for r in range(T + 1, T + 1 + k):
                add(r, DIR[F])
            cur_x, cur_t, face = X + 1.5 * k, T + 19, F
        elif st[0] == "slash":
            _, r, f, turn = st
            if turn:
                add(r - 2, DIR[f]); add(r - 1, DIR[f])
                cur_x += 1.5 * f   # the 2-row tap moves 1.5 px per row (only 1 row of motion seen before the slash)
                cur_x += 1.5 * f
            add(r, "B"); add(r + 1, "B")
            lastslash = r
            face = f
        elif st[0] == "jump":
            T, X, F, hold, cnt = st[1:6]
            mode = st[6] if len(st) > 6 else None
            j = round((X - cur_x) / 1.5)
            if j:
                d = 1 if j > 0 else -1
                for r in range(T - abs(j), T):
                    add(r, DIR[d])
            add(T, "A"); add(T + 1, "A")
            h = M.HOLDS.index(tuple(hold))
            last = max(swings[-1] if swings else -99, lastslash)
            if mode is None:
                sw, hs, xi, V = M.sim_jump(T, X, F, h, last)
            else:
                import jqplan2
                sw, hs, xi, V = jqplan2.sim_jump(T, X, F, h, last, 1 if mode >= 1 else 0, walked=bool(j))
                if mode >= 2:                      # ground slash before the jump
                    r = T - 8 - (mode - 2) * 4
                    add(r, "B"); add(r + 1, "B")
            for i in range(0, NI + 1):
                if V[i] > 0:
                    add(T + i, DIR[F])
                elif V[i] < 0:
                    add(T + i, DIR[-F])
            swings += sw
            cur_x, cur_t, face = float(xi[NI]), T + NI, F
    for s in swings:
        add(s - 1, "Down"); add(s, "Down", "B"); add(s + 1, "B")
        for b in ("Left", "Right"):
            rows.get(s - 1, set()).discard(b); rows.get(s, set()).discard(b)
    n = max(rows) + end_extra
    out = [set(rows.get(r, ())) for r in range(1, n + 1)]
    # repair: one-row gaps between presses of the same direction are filled (release >= 2), one-row presses held 2
    for b in ("Left", "Right", "A", "B", "Down"):
        for i in range(1, n - 1):
            if b in out[i - 1] and b not in out[i] and b in out[i + 1]:
                opp = {"Left": "Right", "Right": "Left"}.get(b)
                if opp is None or opp not in out[i]:
                    out[i].add(b)
    return [tuple(sorted(r)) for r in out], swings


if __name__ == "__main__":
    import a56_common as C
    from ng.inputs import read_inputs
    plan = json.loads(Path(sys.argv[1]).read_text())
    want, swings = plan_rows(plan["steps"])
    import os
    MD = os.environ.get("BOSS") == "mdevil"
    START = "ref4751/19_6-4a_control" if MD else "tmp/a56r2_64b_control"
    hist = [] if MD else list(read_inputs(P / "logs/a56_6-4a_b11.inputs.txt"))[-1700:] + [()] * 151
    en = C.Enforcer(hist)
    rr = [en.emit(r, retry=0) for r in want]
    diff = [(i + 1, want[i], rr[i]) for i in range(len(rr)) if set(want[i]) != set(rr[i])]
    print("rows", len(rr), "enforcer changes", len(diff), diff[:12])
    e = C.open_emu("r4_jqrows.log")
    try:
        from ng.mode import TICKS
        e.tick(TICKS)
        F = dict(e.fields); F.update(jx=(0x466 if MD else 0x467), a83=0x83, bh6=0x496); e.set_fields(F)
        s0 = e.load(START)
        tr = C.play_trace(e, rr)
        prev = 16 if not MD else 14
        for i, t in enumerate(tr):
            r = i + 1
            BH = "bh6" if MD else "boss_real"
            hit = t[BH] < prev
            if r in swings or hit or t["anim"] == 11 or (t["hp"] < (tr[i - 1]["hp"] if i else 16)):
                print(r, "R", t["x"], t["y"], "f84", hex(t["rflags"]), "anim", t["anim"], "J", t["jx"], "dx", t["jx"] - t["x"],
                      "bhp", t[BH], "hp", t["hp"], "HIT" if hit else "", "swing" if r in swings else "")
            prev = t[BH]
            if t[BH] == 0 or (MD and t["bosshp"] == 0):
                print("KILL at row", r, "frame", t["frame"])
                break
        if "--save" in sys.argv:
            nm = sys.argv[sys.argv.index("--save") + 1]
            C.save_rows(P / "states" / "tmp" / f"{nm}.inputs.txt", rr[:i + 1], f"jqrows {sys.argv[1]}")
    finally:
        e.close()
