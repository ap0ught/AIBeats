"""Clinger-Winger: per-corner choice of the switch distance D. From the state entering segment s, try each D, ride
until the toad is on segment s+2 (i.e. through corner s+1), keep the fastest surviving D. Output: the full input
list -> knowledge/l11_greedy.json, bookmark L11_ridden (off the unicycle / end of the maze)."""
import json, sys
from toads.emulator import BizHawk, PROJECT
SEGS = json.loads((PROJECT / "knowledge" / "l11_segments.json").read_text())
DS = [2, 4, 6, 8, 10, 12, 16, 20, 24]

def pos(r):
    return r[0x3FD] + 256 * r[0x3EE], (r[0x89] + 256 * r[0x8A] + 32768) % 65536 - 32768

def step_policy(e, st, D):
    """one frame of the controller; st = dict(s, prev, pre); returns (btn, event)"""
    r = e.ram_all(); x, cy = pos(r); an = r[0x3B5]
    if st["pre"] and an in (100, 101, 102, 103):
        st["pre"] = False
    dx, dy = x - st["prev"][0], cy - st["prev"][1]; st["prev"] = (x, cy)
    d = None
    if abs(dx) > abs(dy): d = "Right" if dx > 0 else "Left"
    elif abs(dy) > abs(dx): d = "Up" if dy < 0 else "Down"
    s = st["s"]
    if s + 1 < len(SEGS) and d == SEGS[s + 1][1] and abs(x - SEGS[s + 1][2]) + abs(cy - SEGS[s + 1][3]) <= 24:
        st["s"] = s = s + 1
    btn = (SEGS[s][1],)
    if s + 1 < len(SEGS):
        _, nd, nx, ncy = SEGS[s + 1]
        if abs(x - nx) + abs(cy - ncy) <= D:
            btn = (nd,)
    if st["pre"]:
        btn = ("Right",)
    return btn

e = BizHawk(log_name="l11greedy.log")
e.load("L11_start"); e.step((), 2)
st = dict(s=0, prev=pos(e.ram_all()), pre=True)
ins = []
# ride with a safe default until on segment 1
while st["s"] < 1:
    b = step_policy(e, st, 8); e.step(b, 1); ins.append("+".join(b))
while st["s"] < len(SEGS) - 1:
    s0 = st["s"]; base = e.msave(); best = None
    for D in DS:
        e.mload(base); st2 = dict(st); seq = []; ok = False
        for k in range(1500):
            b = step_policy(e, st2, D); e.step(b, 1); seq.append("+".join(b))
            if e.ram_all()[0x51A] < 47:
                break
            if st2["s"] >= min(s0 + 2, len(SEGS) - 1):
                ok = True; break
        if ok and (best is None or len(seq) < len(best[1])):
            best = (D, seq, dict(st2))
    if best is None:
        print(f"segment {s0}: every D dies", pos(e.ram_all()), flush=True); break
    # commit only up to entering segment s0+1 (so the next corner's D is chosen fresh)
    D, seq, _ = best
    e.mload(base); st3 = dict(st); committed = []
    for b in seq:
        e.step(tuple(v for v in b.split("+") if v), 1); committed.append(b)
        # re-run the policy bookkeeping to track the segment index
        r = e.ram_all(); x, cy = pos(r)
        dx, dy = x - st3["prev"][0], cy - st3["prev"][1]; st3["prev"] = (x, cy)
        d = None
        if abs(dx) > abs(dy): d = "Right" if dx > 0 else "Left"
        elif abs(dy) > abs(dx): d = "Up" if dy < 0 else "Down"
        if st3["s"] + 1 < len(SEGS) and d == SEGS[st3["s"] + 1][1] and abs(x - SEGS[st3["s"] + 1][2]) + abs(cy - SEGS[st3["s"] + 1][3]) <= 24:
            st3["s"] += 1
        if r[0x3B5] in (100, 101, 102, 103):
            st3["pre"] = False
        if st3["s"] >= s0 + 1:
            break
    ins += committed; st = st3
    e.mfree(base)
    if s0 % 5 == 0:
        print(f"segment {s0} -> {st['s']}: D {D}, total {len(ins)} frames, pos {pos(e.ram_all())}", flush=True)
print("done at segment", st["s"], "frames", len(ins), pos(e.ram_all()), "anim", e.ram_all()[0x3B5], flush=True)
(PROJECT / "knowledge" / "l11_greedy.json").write_text(json.dumps(ins))
e.save("L11_ridden"); e.close()
