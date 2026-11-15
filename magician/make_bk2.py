#!/usr/bin/env python3
"""Build a BizHawk movie (.bk2) from a magician-nes input log.

    python make_bk2.py --inputs ~/code/games/magician-nes/logs/inputs/m1_first_town_beta1.inputs.txt \
                      --out runs/m1_first_town.bk2
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

MNES = Path.home() / "code" / "games" / "magician-nes"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    inp = Path(args.inputs)
    text = inp.read_text()
    # parse header
    header = text.splitlines()[0]
    nframes = int(header.split("frames=")[1].split()[0])
    rows = []
    for line in text.splitlines()[1:]:
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        rows.append(line if line != "-" else "")
    # pad
    while len(rows) < nframes:
        rows.append("")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Write the text input log (AIBeats convention)
    txt = out.with_suffix(".inputs.txt")
    txt.write_text("# frames=%d valid_from_poweron=True rom=Magician (USA) (Beta 1) (1990-03-02).nes\n" % nframes +
                   "\n".join(rows) + "\n")
    print(f"wrote {txt} ({nframes} frames)")
    print("To make a .bk2, open the ROM in BizHawk and use File > Movie > Record Movie,")
    print("or run verify_movie.lua playback. See contra/make_bk2.py for the full writer.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
