"""Track C: write one variant of a segment: extra presses on given indices, cut on the frame the toad is set down in the next level.
    python u17c_mk.py <segment>[@entry bookmark] <out (C...)> <next level byte> <index>:<button> [<index>:<button> ...]
    -> logs/pbeam_<out>.json (bookmark = the entry bookmark), states/<out>_end0b.State; prints length, end state, banned presses"""
import sys

from u17c_lib import *

spec, out, LVL = sys.argv[1], sys.argv[2], int(sys.argv[3])
SEG, _, BM = spec.partition("@")
sj = segj(SEG)
BM = BM or sj["bookmark"]
sg = seg(SEG)
pr = {int(a.split(":")[0]): a.split(":")[1] for a in sys.argv[4:]}
n = len(sg)
tail_input = lambda i: sg[i] if i < n else sg[n - 2 + (i - n) % 2]
add = lambda b, btn: b if btn in b.split("+") else (b + "+" + btn).lstrip("+")
e = BizHawk(log_name=f"u17c_mk_{out}.log", fields={"level": 0x10, "x": 0x3FD, "xh": 0x3EE, "hp": 0x51A, "lives": 0x11})
e.load(BM)
full, stage = [], 0
for i in range(n + 40):
    b = add(tail_input(i), pr[i]) if i in pr else tail_input(i)
    assert not banned1(b), (i, b)
    s = e.step(bt(b), 1)
    full.append(b)
    stage = placed_stage(stage, s.level, s.hp, s.x | s.xh << 8, LVL)
    if stage == 3:
        break
assert stage == 3, "the toad was never set down"
e.save(out + "_end0b")
d = dict(sj)
d.update(bookmark=BM, inputs=full, built_from=SEG, sync_press={str(k): v for k, v in pr.items()})
if "placed" in d:
    d["placed"] = d["placed"] - n + len(full)
write_seg(out, d)
lr, ud, st, sel = banned(full)
print(f"wrote pbeam_{out}.json: {len(full)} inputs ({len(full) - n:+d} vs {SEG}) from {BM}, presses {pr}; end {toad(e.ram(0, 0x800))}; Left+Right {lr}, Up+Down {ud}, Start {st}, Select frames {sel}; bookmark {out}_end0b")
e.close()
