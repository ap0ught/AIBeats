"""Run a chain of l4s.py searches, each from the previous one's solved state (bookmark + 2 idle + its inputs).

    python chainrun.py <chain name>

Chains are defined below: (root bookmark, [(next bookmark, [l4s args...], {env})...]). If logs/l4s_<bm>.txt
already says "solved" for a row, the row is not searched again (its bookmark is rebuilt from the json).
Prints one line per row; stops at the first unsolved row.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from toads.emulator import BizHawk

P = Path(__file__).parent
BASE4 = {"L4S_LVL": "4", "L4S_HPMIN": "15", "L4S_ACTS": "rev", "L4S_SPDKEY": "1"}
BASE4S = {"L4S_LVL": "4", "L4S_HPMIN": "15", "L4S_SPDKEY": "1"}
CHAINS = {
    # Level 4 after the ice-ball damage boost through the spikes (lands on ledge 3 at 576,222): to the ice ball
    "l4boost": ("L4r_l3b", [
        ("L4r_b1", ["795", "-83", "300", "reach_down"], BASE4S),          # right along ledge 3, down to the bowl's slope top
        ("L4r_b2", ["585", "-109", "300", "reach_down_left"], BASE4S),    # down the slope to the ice ball (576,30)
    ]),
    # Level 4 after checkpoint 5, the switchback at a sprint (2026-10-01): from platform 2
    "l4direct": ("L4r_onp2b", [
        ("L4r_d1", ["735", "17", "300", "reach"], BASE4),                 # the upper ledge's right end
        ("L4r_d2", ["590", "-192", "300", "reach_down_left"], BASE4),     # down, left along the lower ledge, onto ledge 3
        ("L4r_d3", ["795", "-83", "300", "reach_down"], BASE4),           # right along ledge 3, down to the bowl's slope
        ("L4r_d4", ["585", "-109", "300", "reach_down_left"], BASE4),     # down the slope to the ice ball (576,30)
    ]),
}


def solved(bm):
    log = P / "logs" / f"l4s_{bm}.txt"
    return log.exists() and "solved" in log.read_text(errors="ignore") and "unsolved" not in log.read_text(errors="ignore")


def main(name):
    root, rows = CHAINS[name]
    for out, args, env in rows:
        log = P / "logs" / f"l4s_{root}.txt"
        if not solved(root):
            if log.exists() and not any(w in log.read_text(errors="ignore") for w in ("solved", "unsolved", "Traceback")):
                while not any(w in log.read_text(errors="ignore") for w in ("solved", "unsolved", "Traceback")):
                    time.sleep(15)                      # a search on this root is already running: wait for it
            else:
                with open(log, "w") as f:
                    subprocess.run([sys.executable, "l4s.py", root] + args, cwd=P, env=dict(os.environ, **env), stdout=f, stderr=subprocess.STDOUT)
        if not solved(root):
            print(root, "->", out, "UNSOLVED", flush=True)
            return
        ins = json.load(open(P / "knowledge" / f"l4s_{root}.json"))
        e = BizHawk(log_name="chainrun.log")
        e.load(root)
        e.step((), 2)
        for b in ins:
            e.step(tuple(v for v in b.split("+") if v), 1)
        m = e.ram(0, 0x800)
        e.save(out)
        e.close()
        print(f"{root} -> {out}: {len(ins)} frames, toad {m[0x3FD] | m[0x3EE] << 8},{m[0x439]} hp {m[0x51A]} lives {m[0x11]} cp {m[0x585]}", flush=True)
        root = out


if __name__ == "__main__":
    main(sys.argv[1])
