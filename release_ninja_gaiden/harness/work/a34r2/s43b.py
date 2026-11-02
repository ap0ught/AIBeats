"""4-3b hand route sweep: chimney between the box's left face and the left wall onto the box top."""
import sys, itertools, json
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
C8 = [("Left", "A"), ("Left", "A")] + [("Right",)] * 6
e = K.open_emu("a34r2_s43b.log")
res = []
try:
    e.load("ref4751/10_4-3_control")
    pre = K.load_rows("b43_pre")
    s = e.run(pre)
    rows0 = list(pre)
    while s.frame < 19110:
        s = e.step((), 1); rows0.append(())
    K.save_rows("r2_43b_entry", rows0, "b43_pre + blank rows to 19110 (4-3b entry, Ryu clinging x 91 y 232)")
    f0 = s.frame
    base = e.msave()
    for n, c9, k, w, a2 in itertools.product(range(0, 9), (0, 1), range(4, 16, 2), (0, 2), (0, 1)):
        rows = C8 * n
        if c9 and n:
            rows = rows[:-1]
        rows += [("Left", "A"), ("Left", "A")] + [("Left",)] * k + [()] * w
        rows += [("Right", "A")] * 2 + [("Right",)] * (40 if not a2 else 3)
        if a2:   # second chimney bounce: back to the box face, then left wall again, then right
            rows += [("Left", "A")] * 2 + [("Left",)] * k + [("Right", "A")] * 2 + [("Right",)] * 40
        L = K.Legal(rows0)
        leg = K.greedy_legal(rows, L)
        e.mload(base)
        e.trace(True); e.run(leg); tr = e.last_trace; e.trace(False)
        top = next((i for i, s in enumerate(tr) if s["y"] <= 146 and not (s["rflags"] & 4) and s["x"] >= 97), None)
        dead = any(s["y"] >= 248 for s in tr[: (top or len(tr))])
        if top is not None and not dead:
            res.append((f0 + top + 1, tr[top]["x"], tr[top]["y"], tr[top]["hp"], n, c9, k, w, a2)); print("ok", res[-1], flush=True)
    res.sort()
    for r in res[:15]:
        print(r, flush=True)
    json.dump(res[:50], open("work/a34r2/s43b.json", "w"))
finally:
    e.close()
