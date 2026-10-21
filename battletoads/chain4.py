"""Chain of l4s searches for the new Level 4 line after the broken checkpoint-6 barrier (2026-10-02):
L4r_bardead -> left ledge -> shaft bottom -> slope -> across the ledges to the checkpoint-7 ledge.
Each row: (root bookmark, out bookmark, l4s args, env). A solved row is not searched again.

    python chain4.py
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from toads.emulator import BizHawk

P = Path(__file__).parent
BASE = {"L4S_LVL": "4", "L4S_SPDKEY": "1"}
ROWS = [
    ("L4r_bardead", "L4r_left2", ["185", "-36", "400", "reach_left"], BASE),          # over pillars C and B and the V-dip to the left ledge
    ("L4r_left2", "L4r_shaft", ["61", "-90", "400", "reach_down_left"], BASE),        # over pillar A and the urchins, down the shaft
    ("L4r_shaft", "L4r_slope", ["322", "-130", "400", "reach_down"], BASE),           # down the snowball slope to the first ledge
    ("L4r_slope", "L4r_plats", ["611", "0", "400", "reach"], BASE),                   # across the ledges/platform to the barrier ledge
]


def main():
    for root, out, args, env in ROWS:
        log = P / "logs" / f"l4s_{root}.txt"
        js = P / "knowledge" / f"l4s_{root}.json"
        txt = log.read_text(errors="ignore") if log.exists() else ""
        if not ("solved" in txt and "unsolved" not in txt and js.exists() and " ".join(args) in txt):
            with open(log, "w") as f:
                f.write("args " + " ".join(args) + "\n")
                f.flush()
                subprocess.run([sys.executable, "l4s.py", root] + args, cwd=P, env=dict(os.environ, **env), stdout=f, stderr=subprocess.STDOUT)
            txt = log.read_text(errors="ignore")
        if "solved" not in txt or "unsolved" in txt:
            print(root, "->", out, "UNSOLVED", flush=True)
            return
        ins = json.load(open(js))
        e = BizHawk(log_name="chain4.log")
        e.load(root)
        e.step((), 2)
        for b in ins:
            e.step(tuple(v for v in b.split("+") if v), 1)
        m = e.ram(0, 0x800)
        e.save(out)
        e.close()
        print(f"{root} -> {out}: {len(ins) + 2} frames, toad {m[0x3FD] | m[0x3EE] << 8},{m[0x439]} hp {m[0x51A]} lives {m[0x11]} cp {m[0x585]} optr {m[0xB7] | m[0xB8] << 8:x}", flush=True)


if __name__ == "__main__":
    main()
