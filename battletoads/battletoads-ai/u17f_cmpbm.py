"""Final builder probe: does a level read the dice?  One segment from its bookmark, twice: as it is and with one extra press
(default Select) on an early frame; the toad compared frame by frame.
    python u17f_cmpbm.py <tag> <segment>[@bookmark] <index>:<button> [<index>:<button> ...]
    -> logs/fix/u17f_cmpbm_<tag>.txt: frames where the toad key (x, height, depth, z, health, level byte, lives) or the score differ,
       frames where the dice $25-$28 differ, and every level-byte change of both runs.   No memory writes."""
import sys

from u17f_lib import *

tag, spec = sys.argv[1], sys.argv[2]
pr = {int(a.split(":")[0]): a.split(":")[1] for a in sys.argv[3:]}
name, _, bm = spec.partition("@")
sj, sg = segj(name), seg(name)
bm = bm or sj["bookmark"]
log = Log(f"u17f_cmpbm_{tag}.txt")
e = BizHawk(log_name=f"u17f_cmpbm_{tag}.log")


def run(presses):
    e.load(bm)
    out, lv, prev = [], [], None
    for i, b in enumerate(sg):
        if i in presses:
            b = (b + "+" + presses[i]).lstrip("+")
            assert not banned1(b)
        e.step(bt(b), 1)
        m = e.ram(0, 0x800)
        out.append((key(m), bytes(m[0x5F4:0x5FA]), bytes(m[0x25:0x29])))
        if m[0x10] != prev:
            lv.append((i + 1, m[0x10]))
        prev = m[0x10]
    return out, lv, toad(m)


a, la, ta = run({})
b, lb, tb = run(pr)
nk = [i + 1 for i in range(len(a)) if a[i][:2] != b[i][:2]]
nd = [i + 1 for i in range(len(a)) if a[i][2] != b[i][2]]
log(f"{name} from {bm}, {len(sg)} inputs; extra presses {pr}")
log(f"  as it is: level-byte changes {la}; end {ta}")
log(f"  with the presses: level-byte changes {lb}; end {tb}")
log(f"  toad key / score differ on {len(nk)} frames (first {nk[0] if nk else None}); dice differ on {len(nd)} frames (first {nd[0] if nd else None})")
e.close()
