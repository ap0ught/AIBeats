"""Where does OUR screen go black at each level end? (2026-10-02)

The record's level-end times are read from its video as the first black frame of each transition
(knowledge/wr_splits.json). To compare like with like, find the same frame in our run: replay a verified route from
power-on and, around every change of the level byte, screenshot every 2nd frame and take the first black one.

    python blackcal.py <route>     -> knowledge/black_<route>.json  [{level byte left, byte_frame, black_frame}]
"""
import json
import sys

from PIL import Image

from toads.emulator import BizHawk, LOGS_DIR, SHOTS_DIR

BACK = 240


def dark(p):
    im = Image.open(p).convert("L").resize((32, 30))
    px = list(im.tobytes())
    return sum(px) / len(px)


def main(route):
    ins = [l.strip().replace(",", "+") for l in open(LOGS_DIR / f"{route}.inputs.txt") if not l.startswith("#")]
    e = BizHawk(log_name="blackcal.log")
    saves = []                                                  # (frame, savestate) every 60 frames, the last 6 kept
    out = []
    lvl = None
    i = 0
    while i < len(ins):
        if i % 60 == 0:
            saves.append((i, e.msave()))
            if len(saves) > 6:
                e.mfree(saves.pop(0)[1])
        e.step(tuple(x for x in ins[i].split("+") if x), 1)
        i += 1
        l = e.byte(0x10)
        if lvl is not None and l != lvl and lvl not in (0, 254, 255):
            f0, sid = saves[0]
            e.mload(sid)
            series = []
            for j in range(f0, min(len(ins), i + 240)):
                e.step(tuple(x for x in ins[j].split("+") if x), 1)
                if j % 2 == 0:
                    series.append((j + 1, dark(e.screenshot("blackcal"))))
            # the first black frame of the transition nearest the byte change
            blacks = [f for f, d in series if d < 6]
            runs = [f for k, f in enumerate(blacks) if k == 0 or blacks[k - 1] < f - 2]
            best = min(runs, key=lambda f: abs(f - i)) if runs else None
            out.append({"left": lvl, "byte_frame": i, "black_frame": best, "runs": runs})
            print(out[-1], flush=True)
            for _, s in saves:
                e.mfree(s)
            saves = []
            # carry on from the end of the window
            i = min(len(ins), i + 240)
            l = e.byte(0x10)
        lvl = l
    json.dump(out, open(f"knowledge/black_{route}.json", "w"), indent=1)
    e.close()


if __name__ == "__main__":
    main(sys.argv[1])
