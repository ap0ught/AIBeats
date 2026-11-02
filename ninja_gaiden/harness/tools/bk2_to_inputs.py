"""Convert a BizHawk NES .bk2 'Input Log.txt' (already unpacked, data only) to the harness input format.

    python -I tools/bk2_to_inputs.py "<dir with Input Log.txt>" <out name>      -> logs/<out name>.inputs.txt

The bk2 log's line k is the input of movie frame k from power-on. The harness numbers rows the same way after
`BizHawk.reset()` (framecount 0, row k -> frame k). After a FRESH LAUNCH the bridge connects at framecount 1
(frame 1 already emulated with no input), so a movie replays there only if its first row is empty: drop row 1.
Power/Reset columns must be empty (a movie that resets mid-way is refused). Controller 1 only.
"""
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))
from ng.inputs import write_inputs  # noqa: E402

KEYS = ("Up", "Down", "Left", "Right", "Start", "Select", "B", "A")   # bk2 NES column order


def read_bk2_log(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        parts = line.strip().strip("|").split("|")
        cmd, p1 = parts[0], parts[1]
        if cmd.strip("."):
            raise SystemExit(f"power/reset used in the movie (row {len(rows) + 1}): {line}")
        if len(parts) > 2 and parts[2].strip("."):
            raise SystemExit(f"controller 2 used (row {len(rows) + 1})")
        rows.append(tuple(k for k, c in zip(KEYS, p1) if c != "."))
    return rows


if __name__ == "__main__":
    src = Path(sys.argv[1])
    if src.is_dir():
        src = src / "Input Log.txt"
    rows = read_bk2_log(src)
    out = write_inputs(PROJECT / "logs" / f"{sys.argv[2]}.inputs.txt", rows,
                       f"from {src.parent.name}/{src.name}; row k = movie frame k; play after reset()")
    print(out, len(rows), "rows; row 1 empty:", rows[0] == ())
