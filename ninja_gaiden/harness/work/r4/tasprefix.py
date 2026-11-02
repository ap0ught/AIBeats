"""Round 4: build a prefix = <base rows> + legalized TAS rows TAS[k0:k1] (Enforcer, retry 0, history = base rows),
play it from <state> and report the first frame where our position leaves the TAS's (|dx| or |dy| > tol, compared
on screen x / y / room), then write logs/r4/<out>.inputs.txt = base + TAS rows up to (div - back) frames.
    python work/r4/tasprefix.py <state> <base rows file|-> <k0> <k1> <out> [--back 2] [--tol 1] [--hist file]
k0 = the TAS frame our base end corresponds to (row TAS[k0] leads to frame k0+1)."""
import csv
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs, write_inputs  # noqa

a = sys.argv[1:]


def opt(n, d):
    if n in a:
        i = a.index(n)
        v = a[i + 1]
        del a[i:i + 2]
        return type(d)(v)
    return d


back = opt("--back", 2)
tol = opt("--tol", 1)
histf = opt("--hist", "")
st, basef, k0, k1, out = a[0], a[1], int(a[2]), int(a[3]), a[4]
if basef != "-" and not (P / basef).exists():
    basef = f"logs/r4/{basef}.inputs.txt"
base = list(read_inputs(P / basef)) if basef != "-" else []
hist = (list(read_inputs(P / histf))[-1800:] if histf else [])
tas = list(read_inputs(P / "logs/tas4751.inputs.txt"))
T = {int(r["frame"]): r for r in csv.DictReader(open(P / "logs/tas4751.trace.csv"))}
en = C.Enforcer(hist + base)
rows = [en.emit(r, retry=0) for r in tas[k0:k1]]
e = C.open_emu(f"r4_tasprefix_{out}.log")
try:
    e.load(st)
    if base:
        e.run(base)
    tr = C.play_trace(e, rows)
    div = None
    for i, t in enumerate(tr):
        R = T.get(k0 + i + 1)
        if R is None:
            break
        def wp(d):
            sc = int(d["scroll_scr"]); sc = sc - 256 if sc >= 128 else sc
            return sc * 256 + int(d["scroll"]) + int(d["x"])
        if int(R["room"]) != t["room"] or abs(wp(R) - wp(t)) > tol or abs(int(R["y"]) - t["y"]) > tol:
            div = i
            print("diverge at TAS frame", k0 + i + 1, "ours", t["room"], wp(t), t["y"], "tas", R["room"], wp(R), R["y"],
                  "our frame", t["frame"], flush=True)
            break
    n = len(rows) if div is None else max(0, div - back)
    write_inputs(P / "logs" / "r4" / f"{out}.inputs.txt", base + rows[:n],
                 f"{basef} + legal TAS rows {k0}..{k0 + n} (from {st})")
    s = tr[n - 1] if n else None
    print("wrote", out, "rows", len(base) + n, "end frame", s and s["frame"], "room", s and s["room"], "x", s and s["x"],
          "y", s and s["y"], "hp", s and s["hp"])
finally:
    e.close()
