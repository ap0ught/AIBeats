"""L12h: compose the new tower segment from the final piece and check it by a plain replay from the Level 12 entry bookmark.
    python l12h_compose.py <final piece> [segment name=L12h] [pad=0]
        -> logs/pbeam_<name>.json {bookmark L11r_end0, inputs, note}, bookmark <name>_end0 (the toad set down in Level 13),
           logs/fix/<name>_compose.txt.  pad = idle frames inserted at the standing moment before the last jump (other dice for the queen).
The inputs = L12g[:base_k] + the piece (which ends on the frame the level byte turns 13, like L12g).
Checks: no Left+Right / Up+Down, no Start, health never below full in Level 12, 4 lives, level 13 on the very last input."""
import json, os, sys
from l12h_lib import *
pn = sys.argv[1]; name = sys.argv[2] if len(sys.argv) > 2 else "L12h"; pad = int(sys.argv[3]) if len(sys.argv) > 3 else 0
assert name.startswith("L12h"), "this track only writes L12h* segments"
p = load_piece(pn); G = seg("L12g")
assert p["base"].startswith("L12h_g_f") and p["base_k"] == int(p["base"].split("_f")[1])
ins = G[:p["base_k"]] + list(p["inputs"])
if pad:
    # the last standing wait before the final hop on to the top spring: L12g has '-' x1 then Right, '-', Right+A x16 (old 8649..); find it from the end
    j = len(ins) - 1
    while j > 0 and not (ins[j] == "Right+A" and ins[j - 1] == "" and ins[j - 2] == "Right" and ins[j - 3] == ""): j -= 1
    assert j > len(ins) - 400, "pad spot not found"
    ins = ins[:j - 3] + [""] * pad + ins[j - 3:]
bad = [i for i, b in enumerate(ins) if ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b) or "Start" in b]
e = BizHawk(log_name=f"fix_{name}_compose.log"); e.load("L11r_end0")
hpmin = 99; lives = set(); lvl13 = None; hurt_at = None
for i, b in enumerate(ins):
    e.step(bt(b), 1); m = e.ram(0, 0x800)
    if m[0x10] == 5:
        if i > 20 and m[0x51A] < 47 and hurt_at is None: hurt_at = i + 1
        if i > 20: hpmin = min(hpmin, m[0x51A])
        lives.add(m[0x11])
    if m[0x10] == 13 and lvl13 is None: lvl13 = i + 1
m = e.ram(0, 0x800)
ok = (not bad) and lvl13 == len(ins) and hurt_at is None and lives == {4}
lines = [f"{name}: {len(ins)} frames (L12g 8880: {8880 - len(ins):+d} saved), pad {pad}",
         f"banned presses: {len(bad)} {bad[:5]}", f"level byte 13 first on input {lvl13} (must be the last, {len(ins)})",
         f"health min in Level 12: {hpmin} (hurt at {hurt_at}), lives seen {sorted(lives)}",
         f"end state: $0B {m[0x0B]} $0C {m[0x0C]} score {bytes(m[0x5F4:0x5FA]).hex()} (L12g_end0: $0B 24 $0C 12 score 020803050500)",
         "VALID" if ok else "NOT VALID"]
print("\n".join(lines), flush=True)
open(FIX / f"{name}_compose.txt", "w").write("\n".join(lines) + "\n")
if ok:
    e.save(f"{name}_end0")
    seg_path = LOGS_DIR / f"pbeam_{name}.json"
    note = ("THE REVOLUTION: up the rotating tower. As L12g to the Hornhead before wind face 2; from there the 1-player TAS's own line, legal: "
            "dash launch off the spring to the pole (face 2 spawns 23 frames sooner), drop as the wind lets go, dash jump to the spring, "
            "the lift where it spawns; the wide-platform Hornhead booted Left; the walker juggled (five blows in the air); the spring's "
            "first lap for face 3; dash launches at faces 3 and 4.||" f"{len(ins)} frames (L12g 8,880)")
    tmp = str(seg_path) + ".tmp"
    if seg_path.exists() and not os.path.exists(str(seg_path) + ".backup"): os.replace(seg_path, str(seg_path) + ".backup")
    json.dump({"bookmark": "L11r_end0", "inputs": ins, "note": note, "slack": 0, "piece": pn, "pad": pad}, open(tmp, "w", encoding="utf-8"))
    os.replace(tmp, seg_path)
    print("wrote", seg_path.name, "and bookmark", f"{name}_end0", flush=True)
e.close()
sys.exit(0 if ok else 1)
