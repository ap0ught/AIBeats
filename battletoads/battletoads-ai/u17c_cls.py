"""Track C probe: the hidden alignment frame by frame through a segment (class = timestamp mod 15 // 5, frame parity, lag counter).
    python u17c_cls.py <segment>[@bookmark] <from index> <tag>   -> logs/fix/u17c_cls_<tag>.tsv
columns: index (inputs done), input, level, $0B, lag counter, PC, ts, class, parity, toad anim, hp"""
import sys

from u17c_lib import *
from u16b_phase import core_of

spec, I0, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3]
SEG, _, BM = spec.partition("@")
sj = segj(SEG)
BM = BM or sj["bookmark"]
sg = seg(SEG)
e = BizHawk(log_name=f"u17c_cls_{tag}.log")
e.load(BM)
out = open(FIX / f"u17c_cls_{tag}.tsv", "w", encoding="utf-8")
for i, b in enumerate(sg, 1):
    s = e.step(bt(b), 1)
    if i < I0:
        continue
    c = core_of(e.save("u17c_cls_" + tag))
    pc, ts, par = c[12] | c[13] << 8, c[4] | c[5] << 8, c[8] & 1
    m = e.ram(0, 0x800)
    out.write(f"{i}\t{b}\t{m[0x10]}\t{m[0x0B]}\t{s.get('lag', -1)}\t{pc:04X}\t{ts}\t{ts % 15 // 5}\t{par}\t{m[0x3B5]}\t{m[0x51A]}\n")
out.close()
e.close()
print("done")
