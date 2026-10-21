"""One-off patch (rule v2): on-demand firing in contra/stages/s3s8_engine.py and wasted-press pruning in
s3s8_fight.py. utf-8, temp file then rename. The files before the patch are *.backup_v2."""
import os
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "contra" / "stages"


def patch(name, reps):
    p = D / name
    s = p.read_text(encoding="utf-8")
    for old, new in reps:
        assert s.count(old) == 1, (name, old[:60], s.count(old))
        s = s.replace(old, new)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(s, encoding="utf-8")
    os.replace(tmp, p)
    print("patched", p)


patch("s3s8_engine.py", [
    ('''for _s in range(10):
    TR[f"b{_s}"] = 0x388 + _s
''', '''for _s in range(10):
    TR[f"b{_s}"] = 0x388 + _s
    TR[f"br{_s}"] = 0x438 + _s          # bullet routine: 1 = flying, >= 2 = hit (rule v2: pellets a press created)


def pellets_born(prev, cur) -> int:
    """Pellets created between two consecutive trace states (a slot that became active, or was reused)."""
    n = 0
    for s in range(10):
        if cur[f"b{s}"] and (not prev[f"b{s}"] or (prev[f"br{s}"] >= 2 and cur[f"br{s}"] < 2)):
            n += 1
    return n


def b_starts(rows, prev_down: bool = False) -> int:
    """New B presses in a list of rows."""
    n = 0
    for r in rows:
        d = "B" in r
        if d and not prev_down:
            n += 1
        prev_down = d
    return n
'''),
    ('''def new_ov() -> dict:
    return {"jumps": [], "aims": [], "nofire": [], "stops": [], "lefts": [], "holds": []}
''', '''def new_ov() -> dict:
    return {"jumps": [], "aims": [], "nofire": [], "stops": [], "lefts": [], "holds": [], "fires": []}
'''),
    ('''def gen(pad: Pad, i0: int, n: int, ov: dict, base=("Right",), fire: bool = True):
    """n rows for segment indices i0..i0+n-1. Policy: `base` held, B pressed as often as the rules allow (2 frames
    down), plus overrides:
''', '''def gen(pad: Pad, i0: int, n: int, ov: dict, base=("Right",), fire=True):
    """n rows for segment indices i0..i0+n-1. Policy: `base` held, B pressed as often as the rules allow (2 frames
    down), plus overrides. fire: True = B at the legal cadence everywhere (the first run's metronome), False =
    never, "demand" (rule v2) = B only inside the `fires` intervals. In every mode a press the Pad refuses (5-frame
    rule, press budget, reserve) is not made.
        fires   [(a, b[, gap])] "demand" mode: B presses may start on rows a..b-1, at least `gap` rows apart
''')
    ,
    ('''            elif p.can_press("B") and not _in(ov["nofire"], i):
                want.add("B")
''', '''            elif not _in(ov["nofire"], i):
                if fire == "demand":
                    f = _in(ov.get("fires", ()), i)
                    if f and (f is True or p.t - p.start["B"] >= f) and p.can_press("B"):
                        want.add("B")
                elif p.can_press("B"):
                    want.add("B")
'''),
])

patch("s3s8_fight.py", [
    ('''from .s3s8_lib import Pad
''', '''from .s3s8_lib import Pad
from .s3s8_engine import pellets_born
'''),
    ('''    jumps: tuple = ()
    next_jump: int | None = None
    score: float = 0.0
    hp: int = 0
''', '''    jumps: tuple = ()
    next_jump: int | None = None
    score: float = 0.0
    hp: int = 0
    np: int = 0            # B presses since the beam's start (rule v2: the fewer the better at equal damage)
'''),
    ('''        out = []
        for (o, aim, mv) in variants:
            rows, p = _child_rows(n, cfg, o, aim, J, mv)
            e.mload(sid_of[id(e)])
            e.run(rows)
            tr = e.last_trace
''', '''        out = []
        for (o, aim, mv) in variants:
            rows, p = _child_rows(n, cfg, o, aim, J, mv)
            pressed = 0
            if o is not None:
                # rule v2: the Pad may have refused the press (5-frame rule, press budget): that child is the
                # "no press" child with a pointless change of aim
                pressed = 1 if (o < len(rows) and "B" in rows[o] and p.start["B"] == n.pad.t + o) else 0
                if not pressed:
                    stats["refused"] = stats.get("refused", 0) + 1
                    continue
            e.mload(sid_of[id(e)])
            e.run(rows)
            tr = e.last_trace
            if pressed and o <= cfg.T - 2:
                # rule v2: a press that created no pellet (no bullet slot was free) is pure waste under the
                # sustained limits: the game is where the "no press" child is, the Pad is worse off
                born = sum(pellets_born(n.last if k == 0 else tr[k - 1], tr[k]) for k in range(o, len(tr)))
                if born == 0:
                    stats["wasted"] = stats.get("wasted", 0) + 1
                    continue
'''),
    ('''            out.append({"o": o, "aim": aim if o is not None else n.aim, "rows": rows, "pad": p, "tr": tr, "kill": kill,
                        "m": m, "J": J})
''', '''            out.append({"o": o, "aim": aim if o is not None else n.aim, "rows": rows, "pad": p, "tr": tr, "kill": kill,
                        "m": m, "J": J, "np": n.np + pressed})
'''),
    ('''                c["busy"] = busy
                cands.append((c["score"], busy, len(cands), n, c))
''', '''                c["busy"] = busy
                cands.append((c["score"], busy, c["np"], len(cands), n, c))
'''),
    ('''            kills.sort(key=lambda z: (z[0], z[1]))
            krow, _, n, c = kills[0]
            rows = n.rows + c["rows"][:c["kill"] + 1]
            log(f"[{cfg.name}] kill at row {krow} (layer {layer}, {stats['children']} children, "
                f"{frames} frames, {time.time() - t0:.0f}s)")
            cleanup()
            return rows, {"kill_row": krow, "layers": layer + 1, "children": stats["children"], "frames": frames,
                          "seconds": round(time.time() - t0)}
''', '''            kills.sort(key=lambda z: (z[0], z[3]["np"], z[1]))
            krow, _, n, c = kills[0]
            rows = n.rows + c["rows"][:c["kill"] + 1]
            log(f"[{cfg.name}] kill at row {krow} (layer {layer}, {stats['children']} children, "
                f"{frames} frames, {time.time() - t0:.0f}s); B presses {c['np']}, children dropped: "
                f"{stats.get('wasted', 0)} with a press that fired nothing, {stats.get('refused', 0)} refused by the Pad")
            cleanup()
            return rows, {"kill_row": krow, "layers": layer + 1, "children": stats["children"], "frames": frames,
                          "seconds": round(time.time() - t0), "presses": c["np"], "wasted_dropped": stats.get("wasted", 0),
                          "refused_dropped": stats.get("refused", 0)}
'''),
    ('''        cands.sort(key=lambda z: (z[0], z[1], z[2]))
''', '''        cands.sort(key=lambda z: (z[0], z[1], z[2], z[3]))
'''),
    ('''        for sc, busy, _, n, c in cands:
            js = tuple(sorted(n.jumps + tuple(c["J"])))
''', '''        for sc, busy, _np, _, n, c in cands:
            js = tuple(sorted(n.jumps + tuple(c["J"])))
'''),
    ('''            return Node(name, n.i + cfg.T, n.rows + c["rows"], c["pad"], c["aim"], s,
                        js, nj, c["score"], c["hp"])
''', '''            return Node(name, n.i + cfg.T, n.rows + c["rows"], c["pad"], c["aim"], s,
                        js, nj, c["score"], c["hp"], c["np"])
'''),
])
