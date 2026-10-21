"""Final builder: write the two segments of a shortened head page found by u17f_head.py.
    python u17f_headmk.py <previous segment> <segment> <out previous (Fk...)> <out (Fk...)> <P> <press index>:<button> <head index>:<button> [...]
        out previous = previous segment + the one press; out = head of (P - 2) frames with the given presses + the segment's inputs after P
No emulator; the proof is u17f_chain.py + assemble.py."""
import sys

from u17f_lib import *

PREV, SEG, OUTP, OUT, P = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
pi, pb = sys.argv[6].split(":")
pi = int(pi)
hp = {int(a.split(":")[0]): a.split(":")[1] for a in sys.argv[7:]}
pj, sj = segj(PREV), segj(SEG)
pv, sg = seg(PREV), seg(SEG)
assert pb not in pv[pi].split("+")
pv2 = list(pv)
pv2[pi] = (pv[pi] + "+" + pb).lstrip("+")
assert not banned1(pv2[pi])
head = [hp.get(i, "") for i in range(P - 2)]
sg2 = head + sg[P:]
d = dict(pj)
d.update(inputs=pv2, built_from=PREV, sync_press={str(pi): pb})
write_seg(OUTP, d)
d = dict(sj)
d.update(inputs=sg2, built_from=SEG, head=[P, P - 2], head_presses=sorted(hp.items()))
write_seg(OUT, d)
print(f"wrote pbeam_{OUTP}.json: {len(pv2)} inputs ({PREV} + {pb} on index {pi}: '{pv[pi]}' -> '{pv2[pi]}'); banned {banned(pv2)}")
print(f"wrote pbeam_{OUT}.json: {len(sg2)} inputs ({len(sg2) - len(sg):+d} vs {SEG}); head presses {sorted(hp.items())}; banned (Left+Right, Up+Down, Start, Select) {banned(sg2)}")
