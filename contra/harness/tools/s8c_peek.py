"""Look at a savestate: Bill, scroll, weapon, Barrier timer, live enemy slots, bullets (read-only).

    python tools/s8c_peek.py <state> [rows to idle with Right held, default 1]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine  # noqa: E402

if __name__ == "__main__":
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    with Engine(1, tag="s8") as eng:
        tr = eng.sim(eng.root(sys.argv[1]), [("Right",)] * n)
        for k, s in enumerate(tr):
            if k in (0, n - 1) or k % 20 == 0:
                en = [(q, hex(s[f"t{q}"]), s[f"h{q}"], s[f"ex{q}"], s[f"ey{q}"]) for q in range(16) if s[f"r{q}"]]
                print(k, "frame", s["frame"], "x", s["x"], "y", s["y"], "pos", s["screen"] * 256 + s["scroll"], "weapon",
                      hex(s["weapon"]), "barrier", s["barrier"], "jump", s["jump"], "enemies", en)
