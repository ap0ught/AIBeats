"""u17v_sheets.py - contact sheets from the verifier's own screenshots (logs/fix/u17v_shots/) -> logs/fix/u17v_sheet_*.png"""
import glob
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

FIX = Path(__file__).resolve().parent / "logs" / "fix"
SH = FIX / "u17v_shots"


def sheet(items, out, cols=6, scale=1.0):
    """items = [(path, label)]"""
    items = [(p, l) for p, l in items if os.path.exists(p)]
    if not items:
        print("no pictures for", out)
        return
    w, h = int(256 * scale), int(224 * scale)
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (cols * (w + 2), rows * (h + 14)), (40, 40, 40))
    d = ImageDraw.Draw(im)
    for k, (p, l) in enumerate(items):
        t = Image.open(p).convert("RGB")
        if scale != 1.0:
            t = t.resize((w, h), Image.NEAREST)
        x, y = (k % cols) * (w + 2), (k // cols) * (h + 14)
        im.paste(t, (x, y + 12))
        d.text((x + 2, y), l, fill=(255, 255, 0))
    im.save(FIX / out)
    print(out, len(items), "pictures", im.size)


def chunks(items, base, n=24, cols=6, scale=1.0):
    for i in range(0, len(items), n):
        sheet(items[i:i + n], f"{base}_{i // n + 1:02d}.png", cols, scale)


def files(prefix):
    fs = sorted(glob.glob(str(SH / (prefix + "*.png"))))
    out = []
    for f in fs:
        m = re.search(r"_f(\d+)(?:_p(\d+))?\.png$", f) or re.search(r"_p(\d+)\.png$", f)
        out.append((f, os.path.basename(f)[len(prefix):-4].lstrip("_")))
    return out


an = json.loads((FIX / "u17v_run1_analysis.json").read_text())
cut1, cut2 = an["cuts_13_254"][:2]
which = sys.argv[1:] or ["all"]


def want(k):
    return "all" in which or k in which


if want("landing"):
    sheet(files("run2_land_"), "u17v_sheet_landing.png", cols=7)
if want("cut1"):
    it = files(f"run3_cut1noinput_f{cut1:05d}_p")
    pick = [x for x in it if int(x[1][-3:]) <= 40 or int(x[1][-3:]) % 30 == 0 or 430 <= int(x[1][-3:]) <= 456]
    sheet([(p, "cut1 +" + l[-3:]) for p, l in pick], "u17v_sheet_cut1_noinput.png", cols=7)
    sheet(files("run2_cut1route_"), "u17v_sheet_cut1_route.png", cols=7)
if want("cut2"):
    a = [(p, "frame " + l[-5:]) for p, l in files("run2_cut2_")][-5:]
    b = [(p, "cut2 +" + l[-3:]) for p, l in files("run2_post_p") if int(l[-3:]) <= 16 or int(l[-3:]) % 10 == 0]
    sheet(a + b, "u17v_sheet_cut2_tbird.png", cols=7)
if want("levels"):
    one = []
    for r in an["levels"]:
        fs = files(f"run2_play_b{r['byte']:02d}_")
        fs = [x for x in fs if r["first"] <= int(x[1][-5:]) <= r["last"]]
        if fs:
            p, l = fs[min(2, len(fs) - 1)]
            one.append((p, f"byte {r['byte']} f{l[-5:]}"))
    sheet(one, "u17v_sheet_levels.png", cols=6)
if want("exits"):
    for r in an["levels"]:
        fs = [x for x in files(f"run2_exit_b{r['byte']:02d}_") if r["last"] - 240 <= int(x[1][-5:]) <= r["last"]]
        sheet(fs, f"u17v_sheet_exit_b{r['byte']:02d}_f{r['last']}.png", cols=7)
if want("entries"):
    for r in an["levels"]:
        fs = [x for x in files(f"run2_entry_b{r['byte']:02d}_") if r["first"] <= int(x[1][-5:]) <= r["first"] + 120]
        sheet(fs, f"u17v_sheet_entry_b{r['byte']:02d}_f{r['first']}.png", cols=9, scale=0.75)
if want("play"):
    for b, name in ((1, "level1"), (3, "turbo"), (4, "arctic"), (8, "karnath"), (7, "level8"), (11, "terra"), (9, "ratrace"),
                    (10, "clinger"), (5, "tower"), (13, "queen")):
        chunks(files(f"run2_play_b{b:02d}_"), f"u17v_sheet_play_{name}")
if want("deaths"):
    sheet(files("run2_death_b03_"), "u17v_sheet_death_turbo.png", cols=8, scale=0.75)
    sheet(files("run2_death_b11_"), "u17v_sheet_death_terra.png", cols=6)
    sheet(files("run2_lives_"), "u17v_sheet_lives.png", cols=6)
if want("pages"):
    names = sorted(set(re.sub(r"_p\d+\.png$", "", os.path.basename(f)) for f in glob.glob(str(SH / "run3_page_*.png"))))
    for nm in names:
        it = files(nm + "_p")
        sheet([(p, nm[10:] + " +" + l[-3:]) for p, l in it], f"u17v_sheet_{nm[5:]}.png", cols=8, scale=0.75)
