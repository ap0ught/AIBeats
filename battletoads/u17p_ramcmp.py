"""NesHawk port of up17 (copy of u17p_ramcmp.py): compare two per-frame RAM captures (core_check_toads.py run) frame for frame, same frame
numbers.    python u17p_ramcmp.py <tagA> <tagB>
Prints how many frames are byte-identical, the first frame that differs and which bytes, and both end SHA-1s. Reads only."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

FIX = Path(__file__).resolve().parent / "logs" / "fix"
a, b = sys.argv[1], sys.argv[2]
A = np.memmap(FIX / f"core_{a}.ram", dtype=np.uint8, mode="r").reshape(-1, 0x800)
B = np.memmap(FIX / f"core_{b}.ram", dtype=np.uint8, mode="r").reshape(-1, 0x800)
sa, sb = (json.loads((FIX / f"core_{t}.json").read_text()) for t in (a, b))
ma, mb = (np.loadtxt(FIX / f"core_{t}.meta.tsv", dtype=np.int64, delimiter="\t") for t in (a, b))
print(f"{a}: {sa['core_info']['core_seen']} {sa['inputs']} {len(A) - 1} frames | {b}: {sb['core_info']['core_seen']} {sb['inputs']} {len(B) - 1} frames")
n = min(len(A), len(B))
neq = A[:n] != B[:n]
bad = np.flatnonzero(neq.any(axis=1))
print(f"frames compared {n - 1} (+ frame 0); byte-identical: {n - len(bad)}; differing: {len(bad)}")
print(f"lag flags equal on all frames: {bool((ma[:n, 3] == mb[:n, 3]).all())}; lag totals {int(ma[:n, 3].sum())} / {int(mb[:n, 3].sum())}")
if len(bad):
    cnt = Counter()
    for f in bad:
        for i in np.flatnonzero(neq[f]):
            cnt[int(i)] += 1
    print("first differing frame", int(bad[0]), "last", int(bad[-1]))
    print("bytes that differ (address: frames):", {f"${k:03X}": v for k, v in cnt.most_common(30)})
    f = int(bad[0])
    print("at the first:", [(f"${int(i):03X}", int(A[f, i]), int(B[f, i])) for i in np.flatnonzero(neq[f])[:20]])
print(f"last frame RAM sha1: {a} {hashlib.sha1(A[n - 1].tobytes()).hexdigest()}  {b} {hashlib.sha1(B[n - 1].tobytes()).hexdigest()}")
print("VERDICT:", "BYTE-IDENTICAL ON EVERY FRAME" if len(bad) == 0 and len(A) == len(B) else "DIFFERENT")
