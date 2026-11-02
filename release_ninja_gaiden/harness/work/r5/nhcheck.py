"""Round 5: replay rows on NesHawk (or Mesen with --mesen <mst>) from a state; print room changes, hp changes and
every k-th frame; optional pad-conflict listing (NesHawk keeps the previous pad).
    python work/r5/nhcheck.py <NesHawk state|--mesen x.mst> <rows file> [--skip n] [--every 50] [--n rows]
--skip n: the first n rows of the file are already contained in the state (not replayed)."""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs, to_mask  # noqa
a = sys.argv[1:]


def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i + 1]; del a[i:i + 2]
        return type(d)(v)
    return d


skip = opt("--skip", 0); every = opt("--every", 50); nmax = opt("--n", 0); mesen = opt("--mesen", "")
rf = a[-1]
for c in (rf, f"logs/r5/{rf}.inputs.txt", f"logs/r4/{rf}.inputs.txt", f"logs/{rf}.inputs.txt"):
    if (P / c).exists():
        rf = P / c
        break
rows = read_inputs(rf)[skip:]
if nmax:
    rows = rows[:nmax]
if mesen:
    from ng.fastcore import MesenEmu
    e = MesenEmu()
    e.load(mesen)
else:
    e = C.open_emu("r5_nhcheck.log")
    e.load(a[0])


def wp(s):
    sc = s["scroll_scr"]; sc = sc - 256 if sc >= 128 else sc
    return sc * 256 + s["scroll"] + s["x"]


try:
    e.trace(True)
    e.run(rows)
    tr = list(e.last_trace)
    prev = None
    conf = 0
    for i, s in enumerate(tr):
        if not mesen and s.get("lagged", 0) == 0 and s["pad"] != to_mask(rows[i]):
            conf += 1
            print("  pad conflict frame", s["frame"], "row", i, "pad", s["pad"], "want", to_mask(rows[i]))
        if prev is None or s["room"] != prev["room"] or s["stage"] != prev["stage"] or s["hp"] != prev["hp"] or i % every == 0 \
                or i == len(tr) - 1:
            print(s["frame"], "stage", s["stage"], "room", s["room"], "wpos", wp(s), "y", s["y"], "hp", s["hp"], "anim", s["anim"])
        prev = s
    print("END frame", tr[-1]["frame"], "conflicts", conf)
finally:
    e.close()
