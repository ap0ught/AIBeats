"""Verifier: compare the per-frame RAM capture of a route with the capture of the earlier, independently verified route
up15, level by level (aligned on the frame the level byte takes the level's value).

    python u16v_compare.py <tag new> <tag ref>
"""
import sys
from pathlib import Path

FIX = Path(__file__).resolve().parent / "logs" / "fix"
ta, tb = sys.argv[1], sys.argv[2]
A = (FIX / f"u16v_{ta}.ram").read_bytes()
B = (FIX / f"u16v_{tb}.ram").read_bytes()
NA, NB = len(A) // 2048, len(B) // 2048


def lv(buf, n):
    out = []
    prev = None
    for f in range(1, n + 1):
        v = buf[(f - 1) * 2048 + 0x10]
        if v != prev:
            out.append((f, v))
        prev = v
    return out


def spans(buf, n):
    ch = lv(buf, n)
    res = []
    for i, (f, v) in enumerate(ch):
        if v in (0, 254, 255):
            continue
        end = ch[i + 1][0] - 1 if i + 1 < len(ch) else n
        res.append((v, f, end))
    return res


sa, sb = spans(A, NA), spans(B, NB)
print(f"{ta}: {NA} frames, {tb}: {NB} frames")
print(f"{'lvl':>3} | {ta+' first-last':>22} len | {tb+' first-last':>22} len | dlen | shift | identical RAM frames from the level's first frame | hp/lives/score at the last frame ({ta} | {tb})")
for (va, fa, ea), (vb, fb, eb) in zip(sa, sb):
    assert va == vb
    la, lb = ea - fa + 1, eb - fb + 1
    n = min(la, lb)
    same = 0
    first_diff = None
    ndiff = 0
    for k in range(n):
        ra = A[(fa + k - 1) * 2048:(fa + k) * 2048]
        rb = B[(fb + k - 1) * 2048:(fb + k) * 2048]
        if ra == rb:
            same += 1
        else:
            ndiff += 1
            if first_diff is None:
                first_diff = (k, [hex(i) for i in range(2048) if ra[i] != rb[i]][:8])
    # also aligned at the END of the level
    same_end = 0
    for k in range(n):
        if A[(ea - k - 1) * 2048:(ea - k) * 2048] == B[(eb - k - 1) * 2048:(eb - k) * 2048]:
            same_end += 1
        else:
            break

    def tail(buf, e):
        o = (e - 1) * 2048
        return f"hp {buf[o + 0x51A]} lives {buf[o + 0x11]} score {''.join(str(buf[o + 0x5F4 + i]) for i in range(6))}"
    print(f"{va:3d} | {fa:6d}-{ea:6d} {la:6d} | {fb:6d}-{eb:6d} {lb:6d} | {la - lb:5d} | {fa - fb:6d} | start-aligned: {same}/{n} equal, first diff at +{first_diff[0] if first_diff else None} {first_diff[1] if first_diff else ''}; end-aligned run of equal frames: {same_end} | {tail(A, ea)} | {tail(B, eb)}")
