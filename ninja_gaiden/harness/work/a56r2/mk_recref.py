"""Turn a record-video route trace (record_trace.py) into a reference usable by a56_solve.py --ref.

    python work/a56r2/mk_recref.py <stage idx> <rec json> <start state frame f0> <name> [--room0 R] [--xoff -2 --yoff 9]
           [--tshift S]
Writes logs/<name>.json (+ .ref.json, + an all-blank inputs file): reference frame k = f0 + t (t = NES frames after
the record's control), position = record's Ryu (abs x = video scroll + screen x + xoff, y = screen y + yoff),
interpolated over missing images; hp/ninpo 0 (no penalty), item = the start state's item (constant).
Calibration (5-1 start vs the TAS trace): RAM x = video x - 2, RAM y = video y + 9.
"""
import json
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages"))
import a56_common as C  # noqa: E402


def opt(a, n, d):
    if n in a:
        i = a.index(n)
        v = a[i + 1]
        del a[i:i + 2]
        return type(d)(v)
    return d


def main():
    a = sys.argv[1:]
    xoff = opt(a, "--xoff", -2)
    yoff = opt(a, "--yoff", 9)
    tshift = opt(a, "--tshift", 0.0)
    room0 = opt(a, "--room0", -1)
    item = opt(a, "--item", 0)
    stage, recf, f0, name = int(a[0]), a[1], int(a[2]), a[3]
    rec = json.load(open(recf))["rows"]
    if room0 < 0:
        room0 = C.tas_trace()[C.tas_stage(stage)["control"]]["room"]
    pts = [(r["t"] + tshift, room0 + r["room"], r["scroll"] + r["sx"] + xoff, r["sy"] + yoff) for r in rec
           if r["sx"] is not None and r["t"] + tshift >= 0 and r["n"] >= 12]
    T = C.tas_trace(); ts = C.tas_stage(stage)
    end = C.tas_stage(stage + 1)["load"] if stage < 21 else 39084
    tfirst = {}
    tent = {}
    for k in range(ts["control"], end):
        tent.setdefault(T[k]["room"], k)
        if k >= tent[T[k]["room"]] + 40:
            tfirst.setdefault(T[k]["room"], C.abs_x(T[k]))
    rent, rfirst = {}, {}
    for p in pts:
        rent.setdefault(p[1], p[0])
        if p[0] >= rent[p[1]] + 17:
            rfirst.setdefault(p[1], p[2])
    r0 = next(q for q in pts if q[1] == room0)
    tfirst[room0] = C.abs_x(T[ts["control"] + int(r0[0])])
    rfirst[room0] = r0[2]
    pts = [(t, room, ax + tfirst.get(room, rfirst[room]) - rfirst[room], y) for t, room, ax, y in pts]
    # drop outliers: jumps > 24 px between consecutive points within 4 frames
    clean = [pts[0]]
    for p in pts[1:]:
        q = clean[-1]
        if p[1] == q[1] and abs(p[2] - q[2]) + abs(p[3] - q[3]) > 12 * max(1.0, p[0] - q[0]):
            continue
        clean.append(p)
    tend = int(clean[-1][0])
    trace = {}
    j = 0
    for t in range(0, tend + 1):
        while j + 1 < len(clean) and clean[j + 1][0] <= t:
            j += 1
        p = clean[j]
        q = clean[j + 1] if j + 1 < len(clean) else p
        if q[1] == p[1] and q[0] > p[0] and t >= p[0]:
            u = (t - p[0]) / (q[0] - p[0])
            ax = round(p[2] + u * (q[2] - p[2]))
            y = round(p[3] + u * (q[3] - p[3]))
        else:
            ax, y = p[2], p[3]
        trace[f0 + t] = {"frame": f0 + t, "stage": stage, "room": p[1], "x": 0, "xsub": 0, "y": y,
                         "scroll": ax % 256, "scroll_scr": ax // 256, "hp": 0, "ninpo": 0, "item": item,
                         "bosshp": 16, "boss_real": 16, "timer": 0, "subtimer": 0}
    load = f0 + tend + 1
    inp = P / "logs" / f"{name}.inputs.txt"
    C.save_rows(inp, [()] * (load - f0), f"blank rows for the record reference {name}")
    (P / "logs" / f"{name}.json").write_text(json.dumps({"start_frame": f0, "inputs": str(inp), "load": load}))
    (P / "logs" / f"{name}.ref.json").write_text(json.dumps({"start": trace[f0], "trace": trace}))
    print(name, "frames", len(trace), "load", load, "points", len(clean), "room0", room0)


if __name__ == "__main__":
    main()
