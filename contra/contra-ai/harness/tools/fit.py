"""Fit a foreign input log to the game from a savestate.

    python tools/fit.py mkstate <inputs.txt> <n rows> <state name>
        play the first n rows from power-on (emulator frame after = n + 1) and save states/<state name>.State
    python tools/fit.py offsets <state> <movie.inputs.txt> <m_lo> <m_hi> [--max N] [--par 4] [--tail K]
        for every m in [m_lo, m_hi]: load the state, play the movie starting at ITS frame m, report how far it gets
    python tools/fit.py show <state> <movie.inputs.txt> <m> [--max N]
        one play, with the per-frame trace written to logs/fit_show.tsv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk, LOGS_DIR  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import F, Pool, play  # noqa: E402


def opt(args, name, default):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return type(default)(v)
    return default


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = args.pop(0)
    core = opt(args, "--core", "NesHawk")
    if mode == "mkstate":
        rows = read_inputs(args[0])[:int(args[1])]
        with BizHawk(log_name="fit_mkstate.log", fields=F, core=core) as e:
            s = e.run(rows)
            e.save(args[2])
            print("saved", args[2], s)
    elif mode == "offsets":
        mx, par = opt(args, "--max", 6000), opt(args, "--par", 4)
        state, movie, lo, hi = args[0], read_inputs(args[1]), int(args[2]), int(args[3])
        ms = list(range(lo, hi + 1))
        with Pool(min(par, len(ms)), core=core, name="fit") as pool:
            res = pool.map(lambda emu, m: play(emu, state, movie[m - 1:m - 1 + mx]), ms)
        for m, r in sorted(zip(ms, res), key=lambda t: t[1].key(), reverse=True):
            print(f"movie frame {m:5d}: {r}")
    elif mode == "show":
        mx = opt(args, "--max", 6000)
        state, movie, m = args[0], read_inputs(args[1]), int(args[2])
        with BizHawk(log_name="fit_show.log", fields=F, core=core) as e:
            r = play(e, state, movie[m - 1:m - 1 + mx], keep_trace=True)
        print(r)
        with open(LOGS_DIR / "fit_show.tsv", "w", encoding="utf-8") as f:
            f.write("i\tmovie_frame\tinput\t" + "\t".join(r.trace[0].keys()) + "\n")
            for i, s in enumerate(r.trace):
                f.write(f"{i + 1}\t{m + i}\t{'+'.join(movie[m - 1 + i])}\t" + "\t".join(str(v) for v in s.values()) + "\n")
