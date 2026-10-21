"""Track C: page at the head of a segment, third stage: BFS head + ONE extra press on one of the first frames after the placement
(before the dice start rolling), to move the fine alignment.
    U17C_HEAD_BM=<true entry bookmark> python u17c_head3.py <segment> <next level byte> <out (C...)> [K=8] [NA=240] [buttons]
needs logs/fix/u17c_head_<out>.json.  -> logs/pbeam_<out>.json (bookmark = the entry), <out>_end0b, logs/fix/u17c_head3_<out>.txt"""
import json
import os
import sys

from u17c_lib import *
from u16b_phase import core_of

SEG, LVL, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
K = int(sys.argv[4]) if len(sys.argv) > 4 else 8
NA = int(sys.argv[5]) if len(sys.argv) > 5 else 240
BTNS = (sys.argv[6] if len(sys.argv) > 6 else "Select,Up,Down,A,B,Left,Right").split(",")
log = Log(f"u17c_head3_{OUT}.txt")
hj = json.load(open(FIX / f"u17c_head_{OUT}.json"))
P = hj["P"]
heads = sorted({tuple(r[4]) for r in hj["results"] if r[3] == "bfs" and (P - r[0]) % 2 == 0 and r[0] < P}, key=len)
sj = segj(SEG)
sg = seg(SEG)
BM = os.environ.get("U17C_HEAD_BM") or sj["bookmark"]
e = BizHawk(log_name=f"u17c_head3_{OUT}.log")


def phase():
    c = core_of(e.save("u17c_phase_" + OUT))
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1


e.load(BM)
for b in sg[:P]:
    e.step(bt(b), 1)
REF = []
for b in sg[P:P + NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
PHN = phase()
for b in sg[P + NA:]:
    e.step(bt(b), 1)
ref_end = bytes(e.ram(0, 0x800))
SKIP = K + 6
hit, n = None, 0
for head in heads:
    for k in range(K):
        for btn in BTNS:
            b0 = sg[P + k]
            if btn in b0.split("+") or banned1(b0 + "+" + btn):
                continue
            e.load(BM)
            for b in head:
                e.step(bt(b), 1)
            same = 0
            for j in range(NA):
                b = sg[P + j]
                if j == k:
                    b = (b + "+" + btn).lstrip("+")
                e.step(bt(b), 1)
                if j < SKIP:
                    continue
                if cut(e.ram(0, 0x800)) != REF[j]:
                    break
                same += 1
            n += 1
            ok = same == NA - SKIP and phase() == PHN
            if same > 20 or ok:
                log(f"  head {[(i, b) for i, b in enumerate(head) if b]} + {btn} on frame {k} after the placement: identical {same}/{NA - SKIP}{'  MERGED' if ok else ''}")
            if ok:
                hit = (head, k, btn)
                break
        if hit:
            break
    if hit:
        break
log(f"variants {n}")
if hit:
    head, k, btn = hit
    rest = list(sg[P:])
    rest[k] = (rest[k] + "+" + btn).lstrip("+")
    full = list(head) + rest
    e.load(BM)
    for b in full:
        e.step(bt(b), 1)
    m = bytes(e.ram(0, 0x800))
    dd = diff(m, ref_end)
    log(f"one piece from {BM}: {len(full)} inputs ({len(full) - len(sg):+d}); end {toad(m)}; RAM bytes differing from {SEG}'s end: {len(dd)}")
    if not dd:
        e.save(OUT + "_end0b")
        d = dict(sj)
        d.update(bookmark=BM, inputs=full, built_from=SEG, head=[P, len(head)], head_presses=[(i, b) for i, b in enumerate(head) if b], extra=[P + k - (P - len(head)), btn])
        write_seg(OUT, d)
        log(f"wrote pbeam_{OUT}.json ({len(full)}); banned {banned(full)}")
else:
    log("NO merging variant")
e.close()
