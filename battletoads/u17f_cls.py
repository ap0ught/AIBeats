"""Final builder probe: the hidden alignment frame by frame through the end of a segment and into the next one.
    python u17f_cls.py <segment>[@bookmark] <from index> <next segment> <frames of it> <tag> [index:button ...]
    -> logs/fix/u17f_cls_<tag>.tsv   columns: index (inputs done), input, level, $0B, lag counter, PC, ts, parity, dice $25-$28, $09, toad anim, hp, $1A
Extra presses index:button are ADDED to the segment's inputs (throwaway probe; nothing is written to a segment).  No memory writes."""
import sys

from u17f_lib import *
from u16b_phase import core_of

spec, I0, NXT, NN, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5]
pr = {int(a.split(":")[0]): a.split(":")[1] for a in sys.argv[6:]}
SEG, _, BM = spec.partition("@")
sj = segj(SEG)
BM = BM or sj["bookmark"]
sg = seg(SEG) + seg(NXT)[:NN]
add = lambda b, btn: b if btn in b.split("+") else (b + "+" + btn).lstrip("+")
e = BizHawk(log_name=f"u17f_cls_{tag}.log")
e.load(BM)
out = open(FIX / f"u17f_cls_{tag}.tsv", "w", encoding="utf-8")
for i, b in enumerate(sg, 1):
    if i - 1 in pr:
        b = add(b, pr[i - 1])
    s = e.step(bt(b), 1)
    if i < I0:
        continue
    c = core_of(e.save("u17f_cls_" + tag))
    pc, ts, par = c[12] | c[13] << 8, c[4] | c[5] << 8, c[8] & 1
    m = e.ram(0, 0x800)
    out.write(f"{i}\t{b}\t{m[0x10]}\t{m[0x0B]}\t{s.get('lag', -1)}\t{pc:04X}\t{ts}\t{par}\t{bytes(m[0x25:0x29]).hex()}\t{m[0x09]:02X}\t{m[0x3B5]}\t{m[0x51A]}\t{m[0x1A]}\n")
out.close()
e.close()
print("done")
