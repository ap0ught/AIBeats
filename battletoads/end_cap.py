"""Capture the whole 2 KB of RAM on every frame of a route's ending (track END, 2026-10-09).

    python end_cap.py up14                       -> logs/fix/endcap_up14.bin (+ .json index), screenshots shots/end_cap/
    python end_cap.py <seg> <bookmark>           -> same for logs/pbeam_<seg>.json replayed from states/<bookmark>.State

From the last ~750 frames before the first level-byte 13->254 change (the cut to the Dark Queen's speech) to the SECOND
13->254 change (the cut to Professor T. Bird, where the leaderboard clock stops). The speech is skipped with A pressed
every other frame from the first frame after the cut (the refined single press lives in end_tail.py).
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR

FIX = LOGS_DIR / "fix"
FIX.mkdir(exist_ok=True)
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)


def capture(tag, e, ins, base, shots=True):
    """e sits at frame `base` (absolute index of the next input = base). Plays ins[base:], then the tail."""
    rows = []                                   # (frame, ram)
    f = base
    prev = e.byte(0x10)
    cut1 = back = cut2 = None
    k = 0
    while True:
        if f < len(ins):
            b = bt(ins[f])
        elif cut1 is not None and back is None:
            b = ("A",) if (f - cut1) % 2 == 0 else ()
        else:
            b = ()
        e.step(b, 1)
        f += 1
        m = e.ram_all()
        rows.append((f, m))
        lv = m[0x10]
        if cut1 is None and prev == 13 and lv == 254:
            cut1 = f
        elif cut1 is not None and back is None and lv == 13:
            back = f
        elif back is not None and prev == 13 and lv == 254:
            cut2 = f
        prev = lv
        if shots and cut1 is not None and (f - cut1) % 10 == 0:
            e.screenshot(f"end_cap/{tag}_f{f:06d}")
        if cut2 is not None:
            k += 1
            if k > 30:
                break
        if f > len(ins) + 4000:
            break
    with open(FIX / f"endcap_{tag}.bin", "wb") as fh:
        for _, m in rows:
            fh.write(m)
    idx = {"tag": tag, "first_frame": rows[0][0], "frames": len(rows), "cut1": cut1, "back": back, "cut2": cut2}
    (FIX / f"endcap_{tag}.json").write_text(json.dumps(idx))
    print(idx, flush=True)
    return idx


if __name__ == "__main__":
    tag = sys.argv[1]
    if len(sys.argv) == 2:
        ins = [l for l in open(LOGS_DIR / f"{tag}.inputs.txt").read().splitlines() if not l.startswith("#")]
        e = BizHawk(log_name=f"end_cap_{tag}.log")
        e.load("cap14_f46000")
        capture(tag, e, ins, 46000)
    else:
        j = json.loads((LOGS_DIR / f"pbeam_{tag}.json").read_text())
        e = BizHawk(log_name=f"end_cap_{tag}.log")
        e.load(sys.argv[2])
        capture(tag, e, j["inputs"], 0, shots=False)
    e.close()
