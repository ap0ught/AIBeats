"""Build a press-history file for a chained start: the TAS rows up to frame F made legal (stand-in for the earlier
acts), then our own legal rows (files given in order), each followed by 150 blank load rows when --blank is given.
    python ng/stages/a56_mkhist.py <F> <out> [inputs files...] [--blank]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a56_common as C  # noqa: E402

if __name__ == "__main__":
    args = sys.argv[1:]
    blank = "--blank" in args
    if blank:
        args.remove("--blank")
    f, out, files = int(args[0]), args[1], args[2:]
    rows = C.legalize(C.tas_rows()[max(0, f - 1900):f])
    for p in files:
        rows += C.read_inputs(p)
        if blank:
            rows += [()] * 150
    C.save_rows(out, rows, f"a56 history: legal TAS to {f} + {files}")
    print(out, len(rows))
