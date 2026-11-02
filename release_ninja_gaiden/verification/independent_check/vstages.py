"""Record video: per-stage on-screen events, measured by the verifier (frame labels from pts; see vid.py).
For each stage: last dark frame / first non-dark frame of the playfield after the stage's black segment, and the
first frame the HUD TIMER digits are drawn. Hints from knowledge/record_events.json only choose the search window.
"""
import json, os, sys
import numpy as np
import vid

HERE = os.path.dirname(os.path.abspath(__file__))
EV = json.load(open(os.path.join(HERE, "..", "..", "knowledge", "record_events.json"), encoding="utf-8"))
FULL = (0, 0, 1920, 1080)


def feats(n0, n1):
    out = {}
    for n, a in vid.frames(n0, n1, FULL, None):
        g = a.astype(np.float32).mean(axis=2)
        play = g[400:1040, 620:1780].mean()
        dig = g[298:324, 950:1060].mean()
        lab = g[298:324, 720:930].mean()      # the word TIMER- (always drawn when the HUD is)
        out[n] = (round(float(play), 1), round(float(dig), 1), round(float(lab), 1))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "trace":
        n0, n1 = int(sys.argv[2]), int(sys.argv[3])
        for n, f in sorted(feats(n0, n1).items()):
            print(n, f)
    elif sys.argv[1] == "stages":
        res = []
        for st in EV["stages"]:
            fp, tf = st["first_picture_f"], st["timer_digits_first_f"]
            F = feats(fp - 12, tf + 6)
            ns = sorted(F)
            # first non-dark playfield frame after a dark one
            first_pic = next((n for n in ns[1:] if F[n][0] > 12 and F[n - 1][0] <= 12), None)
            first_dig = next((n for n in ns[1:] if F[n][1] > 40 and F[n - 1][1] <= 40 and n > (first_pic or 0)), None)
            r = {"stage": st["stage"], "first_picture": first_pic, "timer_digits": first_dig,
                 "json_first_picture": fp, "json_timer_digits": tf}
            res.append(r)
            print(r, flush=True)
        json.dump(res, open(os.path.join(HERE, "record_stage_events.json"), "w"), indent=1)
