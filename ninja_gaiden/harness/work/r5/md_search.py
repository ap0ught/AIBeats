"""Round 5: Masked Devil (6-4a) searches on Mesen from the TAS's 6-4a control (states/mesen/r5/r5_64a.mst, 37278).
    python work/r5/md_search.py fw            r4m1 rows + one Fire Wheel throw (Up+B x2) inserted / overlaid at row t
    python work/r5/md_search.py wm [ninpo]    DEBUG research: item := Windmill ($C9 = 130), ninpo := n (poke), then a
                                              grid of record-like plans (walk, jump, throw in the air, slash cycles)
Kill = first row with $66 (bosshp) == 0. Legal by the a56 Enforcer (history: the 6-3 rows are unknown -> none).
CANDIDATES ONLY (and 'wm' is research: a poked state is never a deliverable)."""
import itertools
import sys
import time
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng import fastcore as F  # noqa
from ng.inputs import read_inputs, write_inputs  # noqa

BASE = [r for r in read_inputs(P / "logs/a56_6-4a_r4m1.inputs.txt")]
H = 200


def kill_row(states):
    for i, s in enumerate(states):
        if s["bosshp"] == 0 and i > 5:
            return i
    return None


def legal(want):
    en = C.Enforcer([])
    return [en.emit(w, retry=0) for w in want]


def run(fc, cands, tag):
    t0 = time.time()
    res = fc.run_batch("s", cands, record="all")
    out = []
    for c, r in zip(cands, res):
        k = kill_row(r.states)
        hp = min(s["hp"] for s in r.states)
        out.append((k if k is not None else 9999, -hp, c))
    out.sort(key=lambda x: (x[0], x[1]))
    print(f"{tag}: {len(cands)} cands in {time.time() - t0:.0f}s; best kills", [(o[0], -o[1]) for o in out[:8]], flush=True)
    return out


def cycle(n, d=()):
    """n slash-cancel cycles: Down | Down+B | B | . | . (5 rows each)"""
    rows = []
    for _ in range(n):
        rows += [("Down",), ("Down", "B"), ("B",) + d, d, d]
    return rows


def main():
    mode = sys.argv[1]
    fc = F.FastCore(log_name="r5_md.log")
    try:
        fc.load_file(P / "states/mesen/r5/r5_64a.mst", "s0")
        if mode in ("wm", "wmi"):
            n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            fc.poke(0xC9, 130)
            fc.poke(0x64, n)
        fc.save("s")
        base = run(fc, [legal(BASE[:H])], "base")
        print("base kill", base[0][0])
        if mode in ("fw", "wmi"):
            cands = []
            for t in range(0, 130):
                for ov in (0, 1):
                    w = list(BASE[:H])
                    if ov:
                        w[t:t + 2] = [("Up", "B")] * 2
                    else:
                        w = w[:t] + [("Up", "B")] * 2 + [()] * 2 + w[t:]
                    cands.append(legal(w[:H]))
            best = run(fc, cands, mode)
            if mode == "wmi":
                # second throw on top of the best single throw
                b1 = best[0][2]
                c2 = []
                for t in range(0, 130):
                    w = list(b1)
                    w[t:t + 2] = [("Up", "B")] * 2
                    c2.append(legal(w[:H]))
                b2 = run(fc, c2, "wmi2")
                if b2[0][0] < best[0][0]:
                    best = b2
        else:
            # plan: walk Right k1, jump (Right+A x2) , drift Right/none, throw Up+B at ta (rows after takeoff),
            # then slash-cancel cycles; second variant: throw from the ground first.
            cands, keys = [], []
            for k1, ta, drift, pre in itertools.product(range(0, 40, 3), range(0, 30, 2), ("Right", None), (0, 1)):
                d = (drift,) if drift else ()
                w = [("Right",)] * k1
                if pre:
                    w += [("Up", "B")] * 2 + [()] * 3
                w += [("Right", "A")] * 2 + [d] * ta + [("Up", "B")] * 2 + [d] * 2 + cycle(30)
                cands.append(legal(w[:H]))
                keys.append((k1, ta, drift, pre))
            best = run(fc, cands, "wm")
        k, nhp, c = best[0]
        write_inputs(P / "logs/r5" / f"r5_md_{mode}_best.inputs.txt", c, f"md_search {mode}: Mesen kill row {k} hp {-nhp}")
    finally:
        fc.close()


if __name__ == "__main__":
    main()
