"""NesHawk port of up17 (copy of u16p_demash.py, defaults changed): the same port built from the verifier's DE-MASHED reference list.

    python u17p_demash.py [port tag = u17p] [capture of the port = u17v1] [de-mashed reference list] [out tag = u17pd]

The port (core_check_toads.py port) feeds the reference's inputs by POLLED frame: NesHawk frame t gets the input of the
reference's k-th polled frame (k = how many frames the game has read the controller so far), with Select toggled on the
polled indices the search chose; from the Queen's last hit on, the tail is end_tail's own (three single presses).
The verifier's de-mashed list (logs/fix/u17v_demashed_up17.inputs.txt) is the reference with the 30-a-second A/B page
mashes reduced to the single presses the game reads; on quickerNES it replays to a byte-identical RAM capture.
This script
  1. rebuilds the port's input list from (reference rows, reference lag flags, the port's own lag flags, the port's
     Select toggles) and checks that it equals logs/fix/core_<port>.inputs.txt frame for frame up to the last hit
     (proof that the mapping is the port's own);
  2. builds the same list from the de-mashed reference rows and writes logs/fix/core_<out>.inputs.txt.
Nothing is claimed for the result here: it has to be replayed from power-on on NesHawk and its RAM compared with the
port's capture (u17p_ramcmp.py).
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FIX = HERE / "logs" / "fix"
ptag = sys.argv[1] if len(sys.argv) > 1 else "u17p"
ctag = sys.argv[2] if len(sys.argv) > 2 else "u17v1"
dpath = HERE / (sys.argv[3] if len(sys.argv) > 3 else "logs/fix/u17v_demashed_up17.inputs.txt")
otag = sys.argv[4] if len(sys.argv) > 4 else "u17pd"
FIRST_POLL = 100                                  # core_check_toads.py's --first-poll default


def read_inputs(path):
    rows = []
    for l in Path(path).read_text().splitlines():
        if l.startswith("#"):
            continue
        rows.append(tuple(x for x in l.replace("+", ",").split(",") if x))
    return rows


psum = json.loads((FIX / f"core_{ptag}.json").read_text())
rtag = psum["ref"]
rsum = json.loads((FIX / f"core_{rtag}.json").read_text())
ref_rows = read_inputs(HERE / rsum["inputs"])
dem_rows = read_inputs(dpath)
assert len(ref_rows) == len(dem_rows), (len(ref_rows), len(dem_rows))
rmeta = np.loadtxt(FIX / f"core_{rtag}.meta.tsv", dtype=np.int64, delimiter="\t")
reflag = rmeta[:, 3]
polled = [f for f in range(FIRST_POLL, len(ref_rows) + 1) if reflag[f] == 0]
idx = {f: i for i, f in enumerate(polled)}
mods = {idx[f] for f in psum["select_toggles_ref_frames"]}
port_rows = read_inputs(FIX / f"core_{ptag}.inputs.txt")
csum = json.loads((FIX / f"core_{ctag}.json").read_text())
assert (HERE / csum["inputs"]).resolve() == (FIX / f"core_{ptag}.inputs.txt").resolve(), "capture is not of the port's list"
cmeta = np.loadtxt(FIX / f"core_{ctag}.meta.tsv", dtype=np.int64, delimiter="\t")
nlag = cmeta[:, 3]
hit = psum["ending"]["last_hit"] if psum.get("ending") else len(port_rows)


ins = {idx[int(f)]: int(n) for f, n in psum.get("insert_before_ref_frames", {}).items()}   # u17p_port.py's re-alignments
skips = {idx[int(f)] for f in psum.get("skip_ref_frames", [])}


def build(rows):
    """u17p_port.Porter2.step, offline: NesHawk frame t gets the row of reference polled index k (Select toggled on the
    port's chosen indices), or an idle row while an inserted poll is due; k moves on only on frames NesHawk polled."""
    out, k, x = [], 0, 0
    for t in range(1, hit + 1):
        while k in skips and k < len(polled) - 1:
            k += 1
            x = 0
        extra = x < ins.get(k, 0)
        if extra:
            b = ()
        else:
            b = rows[polled[k] - 1]
            if k in mods:
                b = tuple(x_ for x_ in b if x_ != "Select") if "Select" in b else b + ("Select",)
        out.append(b)
        if nlag[t] == 0:
            if extra:
                x += 1
            else:
                k += 1
                x = 0
    return out, k


same, k_end = build(ref_rows)
ok = [set(a) for a in same] == [set(b) for b in port_rows[:hit]]
print(f"port {ptag}: {len(port_rows)} frames, last hit {hit}; rebuilt from the reference by polled frame ({k_end} polled, "
      f"{len(mods)} Select toggles, {sum(ins.values())} inserted idle polls, {len(skips)} skipped reference polls): "
      f"equal to the port's list up to the last hit: {ok}")
if not ok:
    for t, (a, b) in enumerate(zip(same, port_rows[:hit]), 1):
        if set(a) != set(b):
            print("  first difference at frame", t, a, b)
            break
    sys.exit("mapping does not reproduce the port: nothing written")
dem, _ = build(dem_rows)
# A press the reference's game never saw can be seen on this core: when a stretch of the game runs a frame or two apart
# from the reference (a blow rolled differently), a mash press meant for a forced walk reaches a frame on which the toad
# still obeys. Such a press is part of this core's run, not turbo padding: it is KEPT. Test: the frame is polled here, the
# de-mash would remove a button, and the game's own pad byte $29 after that frame shows that button.
BIT = {"A": 0x80, "B": 0x40, "Select": 0x20, "Start": 0x10, "Up": 0x08, "Down": 0x04, "Left": 0x02, "Right": 0x01}
CAP = np.memmap(FIX / f"core_{ctag}.ram", dtype=np.uint8, mode="r").reshape(-1, 0x800)
kept = []
if "--no-keep" not in sys.argv:
    for t in range(1, hit + 1):
        gone = set(port_rows[t - 1]) - set(dem[t - 1])
        if gone and nlag[t] == 0 and any(int(CAP[t, 0x29]) & BIT[b] for b in gone):
            kept.append((t, ",".join(port_rows[t - 1]), int(CAP[t, 0x29])))
            dem[t - 1] = port_rows[t - 1]
print(f"presses of the mashed port that this core's game reads (pad byte $29 shows the button) and that therefore stay: "
      f"{len(kept)} frames {[(t, r, hex(v)) for t, r, v in kept]}")
new = dem + port_rows[hit:]
changed = [t for t in range(1, hit + 1) if set(dem[t - 1]) != set(port_rows[t - 1])]
on_lag = sum(1 for t in changed if nlag[t] == 1)
print(f"de-mashed reference {dpath.name}: {len(changed)} frames of the port change ({on_lag} of them are lag frames on NesHawk, "
      f"{len(changed) - on_lag} are frames on which the game reads the controller); first {changed[:5]} last {changed[-5:]}")
removed = sum(len(set(port_rows[t - 1]) - set(dem[t - 1])) for t in changed)
added = sum(len(set(dem[t - 1]) - set(port_rows[t - 1])) for t in changed)
print(f"button-frames removed {removed}, added {added}")


def presses(rows, b):
    return sum(1 for n in range(len(rows)) if b in rows[n] and (n == 0 or b not in rows[n - 1]))


def fastest(rows, b):
    downs = [n + 1 for n in range(len(rows)) if b in rows[n] and (n == 0 or b not in rows[n - 1])]
    best, where, j = 0, None, 0
    for i in range(len(downs)):
        while downs[i] - downs[j] >= 60:
            j += 1
        if i - j + 1 > best:
            best, where = i - j + 1, downs[j]
    return best, where


for b in ("A", "B", "Select"):
    print(f"button {b}: presses {presses(port_rows, b)} -> {presses(new, b)}; most inside one 60-frame window "
          f"{fastest(port_rows, b)} -> {fastest(new, b)}")
ip = FIX / f"core_{otag}.inputs.txt"
tmp = ip.with_suffix(".txt.tmp")
tmp.write_text(f"# frames={len(new)} NesHawk port {ptag} of {rsum['inputs']} rebuilt from the de-mashed list {dpath.name}: "
               f"lag-compensated, {len(mods)} Select toggles\n" + "\n".join(",".join(b) for b in new) + "\n")
tmp.replace(ip)
print("wrote", ip, len(new), "frames")
