"""Play a converted TAS input list from power-on at several frame offsets and report how far each gets.

    python tools/try_tas.py <logs/x.inputs.txt> <core> <offset> [<offset> ...] [--par N] [--stop F]

offset d: the movie's frame m is applied on emulator frame m + d (the bridge only gets control after emulator
frame 1, which is always input-free; movie frames that would land on frame <= 1 are dropped, they must be empty).
Reports per offset: frames at which the level byte ($30) changes, deaths ($B4 bit 0 rising), game over, lag total.
"""
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402

F = {"level": 0x30, "lives": 0x32, "groutine": 0x18, "lroutine": 0x2C, "pstate": 0x90, "death": 0xB4,
     "screen": 0x64, "scroll": 0x65, "gameover": 0x38, "bossdef": 0x3B, "endidx": 0x19}


def shift(rows, d):
    lead = d - 1
    if lead >= 0:
        return [()] * lead + list(rows)
    assert all(r == () for r in rows[:-lead]), "would drop non-empty movie frames"
    return list(rows[-lead:])


def summarize(tr):
    ev = []
    prev = None
    deaths = 0
    for i, s in enumerate(tr):
        f = s["frame"]
        if prev is not None:
            if s["level"] != prev["level"]:
                ev.append(f"f{f}: level {prev['level']}->{s['level']} (lag {s['lag']})")
            if s["groutine"] != prev["groutine"]:
                ev.append(f"f{f}: game routine {prev['groutine']}->{s['groutine']}")
            if (s["death"] & 1) and not (prev["death"] & 1):
                deaths += 1
                ev.append(f"f{f}: DEATH #{deaths} level {s['level']} screen {s['screen']}.{s['scroll']}")
            if s["gameover"] and not prev["gameover"]:
                ev.append(f"f{f}: GAME OVER")
            if s["bossdef"] != prev["bossdef"]:
                ev.append(f"f{f}: bossdef {prev['bossdef']}->{s['bossdef']} level {s['level']}")
        prev = s
    return ev, deaths


def one(path, core, d, stop, out):
    rows = shift(read_inputs(path), d)
    if stop:
        rows = rows[:stop]
    e = BizHawk(log_name=f"try_{Path(path).stem}_{core}_{d}.log", fields=F, core=core)
    try:
        e.trace(True)
        e.run(rows)
        tr = e.last_trace
    finally:
        e.close()
    ev, deaths = summarize(tr)
    out[d] = (ev, deaths, tr[-1])


if __name__ == "__main__":
    args = sys.argv[1:]
    par, stop = 4, 0
    if "--par" in args:
        i = args.index("--par"); par = int(args[i + 1]); del args[i:i + 2]
    if "--stop" in args:
        i = args.index("--stop"); stop = int(args[i + 1]); del args[i:i + 2]
    path, core, offs = args[0], args[1], [int(x) for x in args[2:]]
    out = {}
    for i in range(0, len(offs), par):
        th = [threading.Thread(target=one, args=(path, core, d, stop, out)) for d in offs[i:i + par]]
        for t in th:
            t.start()
        for t in th:
            t.join()
    for d in offs:
        if d not in out:
            print(f"offset {d}: FAILED"); continue
        ev, deaths, last = out[d]
        print(f"=== offset {d:+d}: deaths {deaths}, end {last}")
        for l in ev[:60]:
            print("   ", l)
