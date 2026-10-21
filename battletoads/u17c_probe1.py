"""Track C probe: a segment's inputs replayed from TWO entry bookmarks; per frame which RAM bytes differ.
    python u17c_probe1.py <tag> <segment> <ref bookmark> <new bookmark> [N frames=all] [idle frames before the segment at the new entry=0]
-> logs/fix/u17c_probe1_<tag>.txt"""
import sys
from collections import Counter

from u17c_lib import *

tag, name, bmA, bmB = sys.argv[1:5]
N = int(sys.argv[5]) if len(sys.argv) > 5 else 10 ** 9
IDLE = int(sys.argv[6]) if len(sys.argv) > 6 else 0
log = Log(f"u17c_probe1_{tag}.txt")
ins = seg(name)[:N]
e = BizHawk(log_name=f"u17c_probe1_{tag}.log")
e.load(bmA)
A0 = bytes(e.ram(0, 0x800))
A = []
for b in ins:
    e.step(bt(b), 1)
    A.append(bytes(e.ram(0, 0x800)))
e.load(bmB)
B0 = bytes(e.ram(0, 0x800))
log(f"{name}[:{len(ins)}] from {bmA} (reference) and from {bmB} (+{IDLE} idle frames first)")
log(f"entry: ref {toad(A0)}")
log(f"entry: new {toad(B0)}")
log(f"entry RAM bytes that differ (stack excluded): {[(hex(i), A0[i], B0[i]) for i in diff(A0, B0)]}")
for _ in range(IDLE):
    e.step((), 1)
cnt, firstk, nd, nk = Counter(), None, 0, 0
for i, b in enumerate(ins):
    e.step(bt(b), 1)
    m = bytes(e.ram(0, 0x800))
    d = diff(A[i], m)
    if d:
        nd += 1
        for a in d:
            cnt[a] += 1
    if key(m) != key(A[i]):
        nk += 1
        if firstk is None:
            firstk = i + 1
            log(f"toad key first differs at frame {i + 1}: ref {toad(A[i])} new {toad(m)}; differing bytes {[(hex(a), A[i][a], m[a]) for a in d[:40]]}")
    if i < 14 or (i < 400 and i % 40 == 0) or i % 500 == 0:
        log(f"  frame {i + 1}: {len(d)} bytes differ {[(hex(a), A[i][a], m[a]) for a in d[:16]]}")
log(f"frames with any RAM difference {nd} of {len(ins)}; frames with a toad-key difference {nk} (first {firstk})")
log(f"bytes by number of differing frames: {[(hex(a), c) for a, c in cnt.most_common(40)]}")
log(f"end: ref {toad(A[-1])}")
log(f"end: new {toad(m)}")
e.close()
