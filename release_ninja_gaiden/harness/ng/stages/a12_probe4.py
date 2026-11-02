"""Try legal wall-climb patterns from a TAS frame: python a12_probe4.py <state> <frame_to_reach> pattern..."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng import legal
from ng.emulator import BizHawk
from ng.mode import TICKS

def rows_of(p):
    out = []
    for tok in p.split(","):
        n = 1
        if "*" in tok:
            tok, n = tok.split("*"); n = int(n)
        out += [tuple(x for x in tok.split("+") if x)] * n
    return out

if __name__ == "__main__":
    ref = legal.TasRef()
    st, f = sys.argv[1], int(sys.argv[2])
    with BizHawk(log_name="a12_probe4.log") as e:
        s0 = e.load(st); e.tick(TICKS)
        pre = ref.rows[s0["frame"]:f]
        legal.play(e, pre)
        sid = e.msave()
        for p in sys.argv[3:]:
            e.mload(sid)
            rows = rows_of(p)
            tr = legal.play(e, rows)
            print(p, legal.is_legal(rows))
            print("   ", " ".join(f"{s['frame']}:{s['y']}/{s['scroll']}/{s['coll']}" for s in tr))
