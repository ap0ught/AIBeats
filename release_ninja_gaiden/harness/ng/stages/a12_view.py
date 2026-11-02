"""View TAS rows with trace fields: python ng/stages/a12_view.py a b [fields]"""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def load_trace(name="tas4751"):
    with open(ROOT / "logs" / f"{name}.trace.csv", encoding="utf-8") as f:
        return [{k: (int(v) if k != "input" and v != "" else v) for k, v in r.items()} for r in csv.DictReader(f)]

if __name__ == "__main__":
    a, b = int(sys.argv[1]), int(sys.argv[2])
    fl = (sys.argv[3] if len(sys.argv) > 3 else "stage,room,x,xsub,y,vx,vy,anim,rflags,scroll_scr,scroll,hp,coll").split(",")
    tr = load_trace()
    for r in tr[a - 1:b]:
        print(f"{r['row']:6d} {r['input']:22s}", " ".join(f"{k}={r[k]}" for k in fl))
