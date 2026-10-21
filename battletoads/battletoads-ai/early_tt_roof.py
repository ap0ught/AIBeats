"""EARLY track (2026-10-09): Terra Tubes - the record runs along the ROOF of the block right of the staircase top (the two
bugs hang under that roof at x 824/840, H 6528-6534; logs/fix/tt_hurt.jpg, wr_tt_2.jpg) and drops off its right end
into the blue tank.  Probe from up14 frame 25186 (toad on the left block, (759,6534)): jump right with different holds
and see whether it lands on the roof (H ~6548, x 826-924) without being grabbed, then run right off the end.
    python early_tt_roof.py -> logs/fix/early_tt_roof.txt"""
import itertools, json
from early_tt_run3 import *   # noqa  (F, bt, ROOT, objs)

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name="early_tt_roof.log", fields=F)
e.load("cap14_f25000")
for i in range(25000, ROOT):
    s = e.step(bt(lines[i]), 1)
root = e.msave()
res_all, best = [], None
for dash, xj, gap, a, end in itertools.product((0, 1), (760, 764, 768, 772, 776), (0, 1), (6, 10, 14, 18, 24, 32), ("Right", "RightThenA")):
    e.mload(root)
    t, ph, cnt, ins, r, track, landed, jumps = s, 0, 0, [], None, [], None, 0
    for j in range(240):
        x, H = t.x | t.xh << 8, t.height | t.hh << 8
        if dash and j == 0:
            inp = ()
        elif dash and j == 1:
            inp = ("Right",)
        elif dash and j == 2:
            inp = ()
        else:
            inp = ("Right",)
            if ph == 0 and x >= xj and t.z == 0:
                ph = 1
                if gap:
                    inp = ()
                    ins.append(""); t = e.step(inp, 1)
                    inp = ("Right", "A"); cnt = 1
                else:
                    inp = ("Right", "A"); cnt = 1
            elif ph == 1:
                if cnt < a:
                    inp = ("Right", "A"); cnt += 1
                else:
                    ph = 2
            elif ph == 2 and t.z == 0 and landed is None and H > 6520 and x > 800:
                landed = (j, x, H)
            if landed and end == "RightThenA" and t.z == 0 and x >= 916 and jumps < 8:
                inp = ("Right", "A"); jumps += 1
        t = e.step(inp, 1)
        ins.append("+".join(inp))
        x, H = t.x | t.xh << 8, t.height | t.hh << 8
        if j % 6 == 5:
            track.append((j + 1, x, H, t.z, t.anim))
        if t.anim in (36, 37):
            r = ("grabbed", j + 1, x, H); break
        if t.hp < 47 or t.lives < s.lives:
            r = ("hurt", j + 1, x, H); break
        if t.anim in (98, 99):
            r = ("SWIM", j + 1, x, H, t.camx | t.camxh << 8); break
    r = r or ("end", 240, t.x | t.xh << 8, t.height | t.hh << 8, t.z, t.anim)
    res_all.append((dash, xj, gap, a, end, landed, r, track))
    if r[0] == "SWIM" and (best is None or r[1] < best[0]):
        best = (r[1], ins, r, (dash, xj, gap, a, end))
out = []
stats = {}
for dash, xj, gap, a, end, landed, r, track in res_all:
    k = (r[0], "roof" if landed else "no roof")
    stats[k] = stats.get(k, 0) + 1
out.append(f"stats {stats}")
shown = 0
for dash, xj, gap, a, end, landed, r, track in res_all:
    if (landed or r[0] == "SWIM") and shown < 14:
        out.append(f"dash {dash} jump@{xj} gap {gap} A{a} {end}: roof landing {landed} -> {r}; track {track[:14]}")
        shown += 1
if best:
    json.dump({"from_frame": ROOT, "inputs": best[1], "result": best[2], "params": best[3]}, open(LOGS_DIR / "fix" / "early_tt_swim_best.json", "w"))
    out.append(f"BEST swim: {best[2]} with {best[3]}")
# one example of a grabbed high jump for the record
for dash, xj, gap, a, end, landed, r, track in res_all:
    if r[0] == "grabbed" and a >= 18:
        out.append(f"example grabbed: dash {dash} jump@{xj} gap {gap} A{a}: {r}; track {track[:10]}"); break
print("\n".join(l[:520] for l in out))
open(LOGS_DIR / "fix" / "early_tt_roof.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
e.close()
