"""RAM watcher: play frames from a savestate and print chosen RAM bytes (and/or every changed byte) per frame.

    python tools/ramwatch.py <state name> [--inputs <file> | --hold Right+B] [--frames 120]
                             [--fields x,y,hp,...] [--addrs 0x86,0x0490-0x0497] [--diff] [--shots K] [--csv out.csv]

--fields   names from knowledge/ram.json (default: a compact set); --addrs: extra addresses / ranges
--diff     also list every RAM byte that changed on that frame (addr:old>new), excluding the stack page
--shots K  screenshot every K frames to shots/ramwatch/
Mode word per frame from ng.mode (play / pause / death / bosskill / stageend / cinema / load / other).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, load_fields  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402
from ng.mode import TICKS, mode  # noqa: E402

DEFAULT = "stage,room,timer,subtimer,hp,ninpo,item,lives,x,xsub,y,vy,scroll_scr,scroll,bosshp,rng,pad"


def parse_addrs(spec):
    out = []
    for part in spec.split(","):
        if not part:
            continue
        if "-" in part:
            a, b = (int(x, 0) for x in part.split("-"))
            out += list(range(a, b + 1))
        else:
            out.append(int(part, 0))
    return out


if __name__ == "__main__":
    args = sys.argv[1:]

    def opt(n, d):
        return args[args.index(n) + 1] if n in args else d
    state = args[0]
    frames = int(opt("--frames", 120))
    if "--inputs" in args:
        rows = read_inputs(opt("--inputs", ""))[:frames]
    else:
        h = opt("--hold", "")
        rows = [tuple(x for x in h.split("+") if x)] * frames
    fields = load_fields()
    names = opt("--fields", DEFAULT).split(",")
    extra = parse_addrs(opt("--addrs", ""))
    shots = int(opt("--shots", 0))
    csvp = opt("--csv", "")
    e = BizHawk(log_name="ramwatch.log")
    lines = []
    try:
        e.tick(TICKS)
        e.load(state)
        prev = e.ram_all()
        for i, r in enumerate(rows):
            s = e.step(r, 1)
            ram = e.ram_all()
            vals = " ".join(f"{n}={ram[fields[n]]}" for n in names if n in fields)
            ex = " ".join(f"{a:03X}={ram[a]:02X}" for a in extra)
            line = f"{s.frame} {mode(s):8s} {'+'.join(r) or '.':10s} {vals} {ex}"
            if "--diff" in args:
                ch = [f"{a:03X}:{prev[a]:02X}>{ram[a]:02X}" for a in range(0x800) if ram[a] != prev[a] and not 0x100 <= a < 0x200]
                line += "  | " + " ".join(ch)
            print(line)
            lines.append(line)
            prev = ram
            if shots and i % shots == 0:
                e.screenshot(f"ramwatch/{s.frame:06d}")
        if csvp:
            Path(csvp).write_text("\n".join(lines) + "\n", encoding="utf-8")
    finally:
        e.close()
