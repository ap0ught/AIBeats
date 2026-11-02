"""Acts 5-6: table of every solved stage file (logs/a56_<stage>_<tag>.json) with frames vs the TAS and the record,
plus check_inputs.py on each input file (alone, and with the history it was solved after when known).

    python ng/stages/a56_report.py [tags...]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a56_common as C  # noqa: E402

FPS = 60.0988
RECORD_S = {"5-1": 40.93, "5-2": 40.90, "5-3": 49.67, "5-4": 13.40, "6-1": 26.37, "6-2": 52.47, "6-3": 48.47,
            "6-4a": 13.63, "6-4b": 16.60, "6-5": 12.57}


def main():
    tags = sys.argv[1:]
    rows = []
    for p in sorted((C.PROJECT / "logs").glob("a56_*.json")):
        if p.name.endswith(".ref.json") or p.name.startswith("a56_chain"):
            continue
        j = json.loads(p.read_text())
        if "stage" not in j:
            continue
        tag = p.stem.split("_", 2)[-1]
        if tags and tag not in tags:
            continue
        nm = j["stage"]
        st = C.NAMES.index(nm)
        ev = C.tas_stage(st)
        # our stage time = start (control or control-1) .. next control (= load + 151); the TAS's control..control
        if st < 21:
            ours = (j["load"] + 151) - j["start_frame"] if j.get("load") else None
            tas = C.tas_stage(st + 1)["control"] - ev["control"]
        else:
            ours = j["load"] - j["start_frame"] if j.get("load") else None     # to END seen
            tas = 39530 - ev["control"]
        rec = round(RECORD_S[nm] * FPS)
        chk = subprocess.run([sys.executable, str(C.PROJECT / "check_inputs.py"), j["inputs"]], capture_output=True,
                             text=True).stdout.strip().splitlines()[-1]
        rows.append((nm, tag, j["start"], ours, tas, rec, j.get("verified"), chk, j.get("hp"), j.get("ninpo"),
                     j.get("item")))
    print(f"{'stage':5s} {'tag':6s} {'ours':>5s} {'TAS':>5s} {'rec':>5s} {'vsTAS':>6s} {'vsRec':>6s} verified check  hp np item  start")
    for nm, tag, start, ours, tas, rec, ver, chk, hp, np_, it in rows:
        if ours is None:
            print(f"{nm:5s} {tag:6s} unfinished")
            continue
        print(f"{nm:5s} {tag:6s} {ours:5d} {tas:5d} {rec:5d} {ours - tas:+6d} {ours - rec:+6d} {str(ver):8s} "
              f"{chk.replace('RESULT: ', ''):5s} {hp} {np_} {it}  {start}")


if __name__ == "__main__":
    main()
