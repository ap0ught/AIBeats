"""Track K: beam search for the EARLIEST frame the toad STANDS on the rising head (z 0, not clinging, 10..18 px above the
head's coordinate, carried).  Root = sprint jump at rj + Right+A to the grab; then one frame per step,
pad {-, Right, Left, A, Right+A, Left+A}, per-layer dedupe, ranked by closeness to 'free-falling just above the head top'.
Every standing state found is tested for 6 idle frames (still standing = carried) and saved to
logs/fix/u16k_beam_<rj>_stand<k>.json (inputs from the room root).
    python u16k_beam.py [rj=80] [width=400] [depth=70]"""
import json, sys
from u16k_lib import *

rj = int(sys.argv[1]) if len(sys.argv) > 1 else 80
width = int(sys.argv[2]) if len(sys.argv) > 2 else 400
depth = int(sys.argv[3]) if len(sys.argv) > 3 else 70
ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A")]
e, lines = open_room(f"u16k_beam_{rj}.log")
out = []


def say(s):
    print(s[:300], flush=True)
    out.append(s)


pre = [""] * rj + ["Right", ""]
for b in pre:
    e.step(bt(b), 1)
grab = None
while len(pre) < rj + 40:
    e.step(("Right", "A"), 1)
    pre.append("Right+A")
    t = rd(e)
    if t["an"] in (88, 89):
        grab = len(pre)
        break
say(f"rj {rj}: grab at r+{grab}: x {t['x']} H {t['H']} rel {t['H'] - t['head'][1]}")
layer = [(e.msave(), [])]
found = []
for step in range(depth):
    nxt, seen = [], set()
    for sid, path in layer:
        for a in ACTS:
            e.mload(sid)
            e.step(a, 1)
            t = rd(e)
            if t["hp"] < 47 or not t["head"]:
                continue
            m = t["m"]
            rel = t["H"] - t["head"][1]
            if rel < -30 or t["x"] > 150 or t["x"] < 80:
                continue
            p = path + ["+".join(a)]
            free = t["an"] not in (88, 89)
            if t["z"] == 0 and free and 10 <= rel <= 18:
                # is it carried?  6 idle frames
                keep = e.msave()
                ok = True
                for _ in range(6):
                    e.step((), 1)
                    t2 = rd(e)
                    if not (t2["z"] == 0 and t2["head"] and 10 <= t2["H"] - t2["head"][1] <= 18 and t2["hp"] == 47):
                        ok = False
                        break
                e.mfree(keep)
                if ok:
                    found.append((grab + step + 1, t["x"], rel, p))
                    say(f"  STANDING at r+{grab + step + 1}: x {t['x']} rel {rel} anim {t['an']} facing {t['face']} (carried 6 frames) after {rle(p)[-6:]}")
                    json.dump({"from_frame": ROOT, "inputs": pre + p, "stand_r": grab + step + 1, "x": t["x"], "rel": rel},
                              open(LOGS_DIR / "fix" / f"u16k_beam_{rj}_stand{len(found)}.json", "w"))
                continue
            key = (t["x"], rel, t["z"], t["an"], m[0x4C0], m[0x4CF] // 32, t["spd"] // 16, t["face"])
            if key in seen:
                continue
            seen.add(key)
            rank = -abs(t["x"] - 116) - 2 * max(0, 13 - rel) - 0.5 * max(0, rel - 26) + (8 if free else 0)
            nxt.append((rank, e.msave(), p))
    for sid, _ in layer:
        e.mfree(sid)
    nxt.sort(key=lambda n: -n[0])
    for n in nxt[width:]:
        e.mfree(n[1])
    layer = [(n[1], n[2]) for n in nxt[:width]]
    if step % 5 == 4:
        say(f"  r+{grab + step + 1}: layer {len(layer)}, best rank {nxt[0][0] if nxt else None}, found {len(found)}")
    if len(found) >= 6 or not layer:
        break
say(f"{len(found)} standing states; earliest r+{found[0][0] if found else None}")
open(LOGS_DIR / "fix" / f"u16k_beam_{rj}.txt", "w").write("\n".join(out) + "\n")
e.close()
