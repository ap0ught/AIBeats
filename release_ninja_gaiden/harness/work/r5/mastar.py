"""Round 5: the a34r2 A* (ng/stages/a34r2_astar.py, unchanged) on Mesen (ng.fastcore.MesenEmu) instead of NesHawk.
    python work/r5/mastar.py <stage e.g. 6-2> <states/mesen/r5/x.mst> <prefix rows name|-> <goal> <out> [astar options]
Prefix rows: any of logs/r5|r4|a34/<name>.inputs.txt (rows already contained in the .mst are NOT replayed: give '-'
and pass --hist <rows file> for the legality history). Output logs/r5/<out>.inputs.txt (only the new rows if the
prefix is '-'). CANDIDATES ONLY: verify on NesHawk."""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a34_core as K  # noqa
from ng.fastcore import MesenEmu  # noqa
from ng.inputs import read_inputs  # noqa
NAMES = ["1-1", "1-2", "2-1", "2-2", "2-3", "3-1", "3-2", "3-3", "4-1", "4-2", "4-3", "4-4",
         "5-1", "5-2", "5-3", "5-4", "6-1", "6-2", "6-3", "6-4a", "6-4b", "6-5"]
for i, n in enumerate(NAMES):
    K.BY_NAME.setdefault(n, i)
K.OUT_DIR = P / "logs" / "r5"


def _load_rows(name):
    for c in (name, f"logs/r5/{name}.inputs.txt", f"logs/r4/{name}.inputs.txt", f"logs/a34/{name}.inputs.txt",
              f"logs/{name}.inputs.txt"):
        if (P / c).exists():
            return read_inputs(P / c)
    raise FileNotFoundError(name)


K.load_rows = _load_rows
K.open_emu = lambda log_name: MesenEmu(log_name=log_name)
import a34r2_astar as A  # noqa
A.K = K
A.main()
