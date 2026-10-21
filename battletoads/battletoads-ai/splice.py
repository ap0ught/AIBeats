"""Put a new piece into a segment and re-fit what follows it (2026-10-02).

    python splice.py <segment> <piece json> <out>
        piece json = {a, b, inputs} (fightbeam.py, shortcut searches): the new inputs replace segment[a:b]
        -> logs/pbeam_<out>.json on the SAME bookmark as <segment>: segment[:a] + piece + (segment[b:] re-fitted
           with rngfit.py from the piece's end state: Select re-rolls, wait repairs; no briefing mash here)

The remainder is fitted against the old run's own track from frame b, so everything after the piece is the old
route again, only earlier.   env RNGFIT_IDS / RNGFIT_BYTES are passed through to the fit.
"""
import json
import os
import subprocess
import sys

from toads.emulator import BizHawk, LOGS_DIR


def main(seg, piece, out):
    d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    old = [x.replace(",", "+") for x in d["inputs"]]
    p = json.load(open(piece))
    a, b = p["a"], p["b"]
    e = BizHawk(log_name=f"splice_{out}.log")
    e.load(d["bookmark"])
    for i, x in enumerate(old[:b]):
        if i == a:
            sa = e.msave()
        e.step(tuple(v for v in x.split("+") if v), 1)
    e.save(f"{out}_oldb")                                        # the old run at b: the remainder's own bookmark
    e.mload(sa)
    for x in p["inputs"]:
        e.step(tuple(v for v in x.split("+") if v), 1)
    e.save(f"{out}_newb")
    e.close()
    json.dump({"bookmark": f"{out}_oldb", "inputs": old[b:], "note": ""}, open(LOGS_DIR / f"pbeam_{out}_rest.json", "w"))
    env = dict(os.environ, RNGFIT_MASH="0")
    rc = subprocess.run([sys.executable, "rngfit.py", f"{out}_rest", f"{out}_newb", f"{out}_restfit"], env=env).returncode
    if rc:
        print(f"splice {out}: the remainder did not fit (see above)")
        return 1
    rest = json.load(open(LOGS_DIR / f"pbeam_{out}_restfit.json"))["inputs"]
    ins = old[:a] + list(p["inputs"]) + rest
    json.dump({"bookmark": d["bookmark"], "inputs": ins, "note": d.get("note", "")}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
    print(f"splice {out}: {len(ins)} frames (was {len(old)}; saves {len(old) - len(ins)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
