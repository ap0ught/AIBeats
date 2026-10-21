"""Still frames of the run video for checking by eye.

    python yt/run_qa.py <name> <tag> k1 k2 ...     k = input frame; h<seconds> = that far into the final hold

Writes yt/out/qa_<name>_<tag>_<k>.jpg (960x540)."""
import os
import sys
from pathlib import Path

name, tag, ARGS = sys.argv[1], sys.argv[2], sys.argv[3:]
os.environ["RUN_NAME"] = name
sys.argv = sys.argv[:1]
YT = Path(__file__).resolve().parent
sys.path.insert(0, str(YT))
import run1080b as R  # noqa: E402
import style as S  # noqa: E402

run = R.Run()
base = R.panel_base(run)


def still(k, hold_t=None):
    k = min(k, run.n)
    nes = next(S.nes_frames(R.SRC, run.sync.cidx(k), 1))
    im = base.copy()
    im.paste(R.game_frame(nes, run, k, hold_t=hold_t), (0, 0))
    R.draw_panel(im, run, k)
    return im


for a in ARGS:
    im, lab = (still(run.n, float(a[1:])), f"hold{a[1:]}") if a.startswith("h") else (still(int(a)), a)
    out = S.OUT / f"qa_{name}_{tag}_{lab}.jpg"
    im.resize((960, 540)).save(out, quality=88)
    print(out)
