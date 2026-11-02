"""Probe the 4-3c entry geometry from our prefix (r3_43b_x3): scripted sequences, traced positions."""
import sys

sys.path.insert(0, "ng/stages")
sys.path.insert(0, ".")
import a34_core as K  # noqa: E402

R = lambda *a: tuple(a)  # noqa: E731
C8 = [R("Left", "A")] * 2 + [R("Right")] * 6


def run(e, sid, B, rows, label, every=1):
    e.mload(sid)
    L = K.Legal(B)
    leg = K.greedy_legal(rows, L)
    e.trace(True)
    e.run(leg)
    tr = e.last_trace
    e.trace(False)
    pts = [(x["frame"], K.wpos(x), x["y"], x["rflags"], x["coll"]) for x in tr]
    print("==", label)
    print(" ".join(f"{f}:{w},{y},{rf:x},{c:x}" for f, w, y, rf, c in pts[::every]), flush=True)
    return pts


def main():
    e = K.open_emu("a34r3_probe43c.log")
    try:
        e.load("ref4751/10_4-3_control")
        B = K.load_rows("r3_43b_x3")
        s = e.run(B)
        sid = e.msave()
        # wait for control: run blank frames until the entry picture
        run(e, sid, B, [()] * 100, "blank 100", 2)
        for k in range(36, 84, 4):
            run(e, sid, B, [()] * k + [R("Right")] * 60, f"blank {k} then Right", 2)
        for k in range(30, 70, 6):
            run(e, sid, B, [()] * 23 + [R("Left")] * 6 + [()] * (k - 29) + [R("Right")] * 60,
                f"Left 6 then blank to {k} then Right", 2)
        run(e, sid, B, [()] * 23 + C8 * 12, "C8 x12 on the pillar face", 2)
        for k in (4, 8, 12, 16, 20, 28):
            run(e, sid, B, [()] * 23 + [R("Left", "A")] * 2 + [R("Left")] * k + [()] * 40, f"JO left, Left x{k}", 2)
        # jump off left then right drift back to the pillar (chimney)
        for k in (4, 8):
            run(e, sid, B, [()] * 23 + ([R("Left", "A")] * 2 + [R("Left")] * k + [R("Right")] * 14) * 4,
                f"JO left {k} + Right back x4", 2)
    finally:
        e.close()


if __name__ == "__main__":
    main()
