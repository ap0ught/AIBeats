"""Correct the picture test in chain2/clock_evidence.json (the original is kept unchanged).

The original counted "blue_pixels_in_hud_box" as any pixel with blue > 150 and red < 120 in the box x 16-67,
y 17-32 of the screenshot. That also counts the stage-1 starfield: 3 light-blue pixels (100, 176, 254) sit in the
box on frames 590-593, before any medal is drawn, so the field read 3 there (the independent check noticed it).
The medal's ribbon is a different NES colour, (66, 64, 254) in BizHawk's palette. This script counts only pixels of
exactly that colour, from the same screenshots (chain2/shots/clock/start_f<frame>.png), in the same box:
0 on frames 590-593, 70 on frame 594. START (593 in RAM, 594 seen) and END (34508 / 34509) do not change.

    python fix_clock_evidence.py <chain2 folder> <out.json>
"""
import json
import sys
from pathlib import Path

from PIL import Image

MEDAL_BLUE = (66, 64, 254)
STARFIELD_BLUE = (100, 176, 254)


def counts(png):
    im = Image.open(png).convert("RGB")
    top = 0 if im.size[1] >= 240 else 8
    box = im.crop((16, 17 - top, 68, 33 - top))
    px = [box.getpixel((x, y)) for y in range(box.size[1]) for x in range(box.size[0])]
    return (sum(1 for p in px if p == MEDAL_BLUE), sum(1 for p in px if p == STARFIELD_BLUE),
            sum(1 for p in px if p[2] > 150 and p[0] < 120))


def main():
    c2, out = Path(sys.argv[1]), Path(sys.argv[2])
    ev = json.loads((c2 / "clock_evidence.json").read_text(encoding="utf-8"))
    for r in ev["start_frames"]:
        medal, star, old = counts(c2 / "shots" / "clock" / r["screenshot"])
        assert old == r["blue_pixels_in_hud_box"], (r["frame"], old, r["blue_pixels_in_hud_box"])
        r["blue_pixels_in_hud_box_ORIGINAL_TEST"] = r.pop("blue_pixels_in_hud_box")
        r["medal_blue_pixels_in_hud_box"] = medal
        r["starfield_pixels_in_hud_box"] = star
    sf = ev["start_frames"]
    N = ev["clock"]["start"]["ram"]
    first = next((r["frame"] for r in sf if r["medal_blue_pixels_in_hud_box"] > 0), None)
    before = [r["medal_blue_pixels_in_hud_box"] for r in sf if r["frame"] < first] if first else []
    s = ev["summary"]
    s["medals_first_in_picture_by_blue_pixels_ORIGINAL_TEST"] = s.pop("medals_first_in_picture_by_blue_pixels", None)
    s["medals_first_in_picture_by_medal_colour"] = first
    s["medal_colour_pixels_before_that"] = before
    s["start_ok"] = s["medals_first_in_ppu_oam"] == N + 1 and first == N + 1 and not any(before)
    ev["correction"] = (
        "2026-10-16, release copy. The original field blue_pixels_in_hud_box (blue > 150 and red < 120) counted 3 "
        "starfield pixels (100,176,254) inside its box on frames 590-593, before any medal is drawn. Replaced by "
        "medal_blue_pixels_in_hud_box: pixels of exactly the medal ribbon colour (66,64,254), same screenshots, same "
        "box (x 16-67, y 17-32 of the 240-line picture). Result: 0 on frames 590-593, 70 on 594. START (RAM 593, "
        "seen 594) and END (RAM 34508, seen 34509) are unchanged. The original file is chain2/clock_evidence.json. "
        "The same counts were re-measured on BizHawk's own movie playback of contra_ai_9m24s.bk2 (verify_bk2.py).")
    ev["inputs"] = "contra_ai_9m24s.inputs.txt (= chain2/run_chain2.inputs.txt)"
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(ev, indent=1), encoding="utf-8")
    tmp.replace(out)
    print("start frames:", [(r["frame"], r["medal_blue_pixels_in_hud_box"], r["blue_pixels_in_hud_box_ORIGINAL_TEST"])
                            for r in sf])
    print("summary:", json.dumps(s))


if __name__ == "__main__":
    main()
