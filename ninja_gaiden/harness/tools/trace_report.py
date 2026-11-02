"""Report events from a trace CSV written by tools/trace_run.py: python tools/trace_report.py <name>"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng import clock  # noqa: E402
from ng.emulator import LOGS_DIR  # noqa: E402
from ng.events import analyse  # noqa: E402


def load(name):
    with open(LOGS_DIR / f"{name}.trace.csv", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return [{k: (v if k == "input" else int(v)) for k, v in row.items()} for row in r]


if __name__ == "__main__":
    tr = load(sys.argv[1])
    rep = analyse(tr)
    rep["clock"] = clock.measure(tr)
    (LOGS_DIR / f"{sys.argv[1]}.events.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    for st in rep["stages"]:
        print(f"{st['name']:5s} load {st.get('load')} control {st.get('control')} boss0 {st.get('boss0')} "
              f"next {st.get('control_to_next_control')}")
    print("deaths", rep["deaths"])
    print("cutscenes", [(c["first"], c["last"], c["stage"], c["skipped"]) for c in rep["cutscenes"]])
    print("game lag frames", rep["game_lag_frames"], rep["game_lag_first"][:20], "bizhawk lag", rep["bizhawk_lag_total"])
    print("clock", rep["clock"])
