"""L12h DEBUG probe (pokes on a snapshot only, never in a run): which RAM bytes make the camera scroll 4 px/frame after face 3 leaves,
as in the TAS (f75883), instead of our 1 px/frame (L12g 7445)? Copy ranges of the TAS's RAM into our state and watch the camera."""
import sys
from l12h_lib import *
G = seg("L12g"); t = open(FIX / "tas_l12.ram", "rb").read()
def tasram(f): i = f - 69570; return t[i * 2048:(i + 1) * 2048]
e = BizHawk(log_name="fix_l12h_campoke.log"); e.load("L12h_g_f7250"); run(e, G[7250:7444]); base = e.msave()
ours = e.ram(0, 0x800); T = tasram(75882)
diff = [a for a in range(0x800) if ours[a] != T[a]]
print(len(diff), "differing bytes", flush=True)
def test(addrs):
    e.mload(base)
    for a in addrs: e.poke(a, T[a])
    c0 = rd(e)["cam"]
    for i in range(4): e.step(("Left", "A"), 1)
    return c0 - rd(e)["cam"]
print("no poke:", test([]), "all:", test(diff), flush=True)
# skip obviously unrelated: toad position/camera themselves
skip = set([0x83, 0x84, 0x89, 0x8A, 0x0B, 0x0C, 0xCD, 0x25, 0x26, 0x27, 0x28])
cand = [a for a in diff if a not in skip]
print("without timers/rng/camera:", test(cand), flush=True)
def bis(addrs, depth=0):
    if len(addrs) == 1: return addrs
    h = len(addrs) // 2; A, B = addrs[:h], addrs[h:]
    ra, rb = test(A), test(B)
    print("  " * depth, f"{len(addrs)}: first half ({A[0]:03X}-{A[-1]:03X}) -> {ra}, second ({B[0]:03X}-{B[-1]:03X}) -> {rb}", flush=True)
    out = []
    if ra >= 8: out += bis(A, depth + 1)
    if rb >= 8: out += bis(B, depth + 1)
    if not out and ra < 8 and rb < 8: print("  " * depth, "needs both halves"); return addrs
    return out
r = bis(cand)
print("RESULT", [f"${a:03X}: ours {ours[a]} TAS {T[a]}" for a in r][:40])
e.close()
