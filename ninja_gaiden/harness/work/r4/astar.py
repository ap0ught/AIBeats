"""Round 4 wrapper: run ng/stages/a34r2_astar.py (unchanged) on any stage, rows in/out under logs/r4/.
    python work/r4/astar.py <stage name e.g. 6-2> <start state> <prefix rows name|-> <goal> <out> [astar options]
(prefix/out names are files logs/r4/<name>.inputs.txt; end state states/tmp/a34r2_x/<out>.State)"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a34_core as K  # noqa
NAMES = ["1-1", "1-2", "2-1", "2-2", "2-3", "3-1", "3-2", "3-3", "4-1", "4-2", "4-3", "4-4",
         "5-1", "5-2", "5-3", "5-4", "6-1", "6-2", "6-3", "6-4a", "6-4b", "6-5"]
for i, n in enumerate(NAMES):
    K.BY_NAME.setdefault(n, i)
K.OUT_DIR = P / "logs" / "r4"
import a34r2_astar as A  # noqa
A.main()
