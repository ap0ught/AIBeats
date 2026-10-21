"""Track K: beam search for a toad STANDING on the rising head, from a root given as an input script (from the room root).
One frame per step, pad {-, Right, Left, A, Right+A, Left+A, Down}; ranked toward 'over the head top (x 106..122), at or above
the top (rel >= 14), falling (vy <= 0)'.  Standing = z 0, not clinging, 10..18 above the head's coordinate, kept 6 idle frames.
    python u16k_beam2.py "<n>:<buttons>;..." <tag> [width=300] [depth=36]"""
import json, sys
from u16k_lib import *

spec, tag = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 300
depth = int(sys.argv[4]) if len(sys.argv) > 4 else 36
ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A"), ("Down",)]
pre = []
for part in spec.split(";"):
    n, b = part.split(":")
    pre += [b] * int(n)
e, lines = open_room(f"u16k_beam2_{tag}.log")
out = []


def say(s):
    print(s[:300], flush=True)
    out.append(s)


for b in pre:
    e.step(bt(b), 1)
t = rd(e)
say(f"root r+{len(pre)}: x {t['x']} rel {t['H'] - t['head'][1]} anim {t['an']} spd {t['spd']}")
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
            if rel < -6 or t["x"] > 160 or t["x"] < 88:
                continue
            vy = (m[0x4C0] if m[0x4C0] < 128 else m[0x4C0] - 256) + m[0x4CF] / 256
            p = path + ["+".join(a)]
            if t["z"] == 0 and t["an"] not in (88, 89) and 10 <= rel <= 18:
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
                    found.append((len(pre) + step + 1, t["x"], rel, p))
                    say(f"  STANDING at r+{len(pre) + step + 1}: x {t['x']} rel {rel} anim {t['an']} facing {t['face']} after {rle(p)}")
                    json.dump({"from_frame": ROOT, "inputs": pre + p, "stand_r": len(pre) + step + 1, "x": t["x"], "rel": rel},
                              open(LOGS_DIR / "fix" / f"u16k_beam2_{tag}_stand{len(found)}.json", "w"))
                continue
            key = (t["x"], rel, t["z"], t["an"], m[0x4C0], m[0x4CF] // 32, t["spd"] // 16, t["face"])
            if key in seen:
                continue
            seen.add(key)
            dx = 0 if 106 <= t["x"] <= 122 else min(abs(t["x"] - 106), abs(t["x"] - 122))
            rank = -dx - 3 * max(0, 14 - rel) - 2.5 * max(0.0, vy) + (0.3 * min(rel, 24))
            nxt.append((rank, e.msave(), p, (t["x"], rel, round(vy, 1), t["an"])))
    for sid, _ in layer:
        e.mfree(sid)
    nxt.sort(key=lambda n: -n[0])
    for n in nxt[width:]:
        e.mfree(n[1])
    layer = [(n[1], n[2]) for n in nxt[:width]]
    if step % 4 == 3 and nxt:
        say(f"  r+{len(pre) + step + 1}: layer {len(layer)}, best {nxt[0][0]:.1f} {nxt[0][3]}, found {len(found)}")
    if len(found) >= 5 or not layer:
        break
say(f"{len(found)} standing states; earliest r+{found[0][0] if found else None}")
open(LOGS_DIR / "fix" / f"u16k_beam2_{tag}.txt", "w").write("\n".join(out) + "\n")
e.close()
