"""Build and check a complete Level 9 line with the fast helicopter-shaft descent, and replay the REST of the run behind it (2026-10-10).

    python l9heli_fix_full.py <tag> <rand json> <entry #> <edits json or -> <select old indices a/b/.. or -> [pad]

 1. cap14 bookmark + old inputs up to the piece's root (RAM must equal the old run's);
 2. the piece (a stage-A variant, the hop(s), the run) -> the old run's state T' (old index 8279);
 3. the old inputs 8280..9987 with the corridor repairs (edits), the Select re-rolls and lag frames held (an input is repeated until the
    frame counter ticks) -> the Level 10 entry; the toad's track is compared with the old run at the same old index;
 4. `pad` empty frames, then the old inputs of Levels 10-13 unchanged, compared with the old run's RAM frame for frame (shifted by the gain).
Writes logs/pbeam_L9heli_<tag>.json (bookmark L8c_end0, the complete Level 9 input list) and prints the bookkeeping."""
import json, sys
from l9heli_fix_lib import *
TAG, SRC, EI = sys.argv[1], sys.argv[2], int(sys.argv[3])
EDITS = json.load(open(sys.argv[4])) if sys.argv[4] != "-" else []
SEL = set(int(v) for v in sys.argv[5].split("/") if v not in ("", "-"))
PAD = int(sys.argv[6]) if len(sys.argv) > 6 else 0
DOWN = int(sys.argv[7]) if len(sys.argv) > 7 else 10**9
R = cap(); ins = up14_inputs(); NF = len(ins)
piece = json.load(open(SRC))[EI]; root = piece["root_index"]
FLD = {"x": 0x3FD, "xh": 0x3EE, "h": 0x439, "hh": 0x42A, "z": 0x475, "hp": 0x51A, "lvl": 0x10, "lives": 0x11, "t": 0x0B, "an": 0x3B5, "cp": 0x585}
e = BizHawk(log_name=f"l9heli_fix_full_{TAG}.log", fields=FLD)
goto(e, OFF + root, ins, check=True)
new = [ins[OFF + i].replace(",", "+") for i in range(root)]           # Level 9 inputs so far (L9c index 1..root), unchanged
for b in piece["inputs"]:
    e.step(bt(b), 1); new.append(b)
m = e.ram(0, 0x800); ref = bytes(R[OFF + 8279 - 1])
def okin(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x448], m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x51A])
print(f"T' reached after {len(new)} Level 9 inputs (old 8279, gain {8279 - len(new)}); toad equal to old: {okin(m) == okin(ref)}; $466 {m[0x466]} (old {ref[0x466]})", flush=True)
t = m[0x0B]; k = 8279; lags = []; first = None; hpd = None; end = None
def lstep(b):
    global t
    for _ in range(8):
        e.step(bt(b), 1); new.append(b); mm = e.ram(0, 0x800)
        if mm[0x0B] != t: break
        lags.append(k + 1)
    t = mm[0x0B]; return mm
def trk(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x51A], m[0x10])
while k < 9987:
    ed = [x for x in EDITS if x["A"] == k]
    if ed:
        for b in ed[0]["inputs"]: m = lstep(b)
        k = ed[0]["TGT"]; ref = bytes(R[OFF + k - 1])
        print(f"repair {ed[0]['A']} -> {k}: toad equal to old {okin(m) == okin(ref)}", flush=True); continue
    b = ins[OFF + k].replace(",", "+")
    if (k + 1) in SEL: b = (b + "+Select").lstrip("+")
    if k >= 9650:
        e.step(bt(b), 1); new.append(b); m = e.ram(0, 0x800); t = m[0x0B]
    else:
        m = lstep(b)
    k += 1; ref = bytes(R[OFF + k - 1])
    if end is None and m[0x10] != 11: end = (k, len(new))
    if trk(m) != trk(ref):
        if first is None: first = (k, trk(m), trk(ref))
        if hpd is None and trk(m)[3:] != trk(ref)[3:]: hpd = (k, trk(m), trk(ref))
for _ in range(PAD):
    e.step((), 1); new.append("")
m = e.ram(0, 0x800); ref = bytes(R[OFF + 9987 - 1]); net = 9987 - len(new)
VOL = set(range(0x100, 0x200))
d = [a for a in range(0x800) if m[a] != ref[a] and a not in VOL]
print(f"Level 9: {len(new)} inputs (old 9987) -> NET GAIN {net} frames; lag frames at {lags}; first track diff {first}; first hp/level diff {hpd}; "
      f"level byte left 11 at (old index, new input count) {end}", flush=True)
print(f"Level 10 entry: RAM differs from the old run's in {len(d)} bytes outside the stack: {[(hex(a), m[a], ref[a]) for a in d[:40]]}", flush=True)
bad = [b for b in new if banned(b)]
print("banned presses:", len(bad), flush=True)
out = {"bookmark": "L8c_end0", "inputs": new, "slack": 0, "rerolls": [], "gain_vs_L9c": net,
       "note": "TERRA TUBES with the fast helicopter-shaft descent: as L9c to the ledge above the propeller bugs, then a dash-jump under both bugs "
               "(never grabbed), a free fall down the shaft, a hop to line the toad up, and the old line again from the pool floor; two waits "
               "at the corridor mines.||" + f"{len(new)} frames ({net} fewer than L9c)"}
json.dump(out, open(LOGS_DIR / f"pbeam_L9heli_{TAG}.json", "w"))
# 4. the rest of the run, unchanged
F0 = OFF + 9987; n = 0; fd = None; nd = 0; lv = m[0x10]; cuts = []; prev = m[0x10]; s = None
for F in range(F0, min(NF, F0 + DOWN)):
    s = e.step(bt(ins[F]), 1); n += 1; ref = R[F]
    a = (s.lvl, s.x | s.xh << 8, s.h | s.hh << 8, s.hp, s.lives, s.cp); c = (int(ref[0x10]), int(ref[0x3FD]) | int(ref[0x3EE]) << 8, int(ref[0x439]) | int(ref[0x42A]) << 8, int(ref[0x51A]), int(ref[0x11]), int(ref[0x585]))
    if prev == 13 and s.lvl == 254: cuts.append(F + 1 - net + 0)
    prev = s.lvl
    if a != c:
        nd += 1
        if fd is None: fd = (F + 1, a, c); print("downstream: first difference at old up14 frame", F + 1, "(new frame", F + 1 - net + PAD, ") ours", a, "old", c, flush=True)
print(f"downstream: {n} frames replayed, {nd} differ, first {fd}; final ours level {s.lvl} x {s.x | s.xh << 8} hp {s.hp} lives {s.lives}; 13->254 cuts at new frames {cuts}", flush=True)
if fd is None:
    mm = e.ram(0, 0x800); ref = bytes(R[min(NF, F0 + DOWN) - 1]); d = [a for a in range(0x800) if mm[a] != ref[a]]
    print("final RAM equal to the old run's:", not d, len(d), flush=True)
e.close()
