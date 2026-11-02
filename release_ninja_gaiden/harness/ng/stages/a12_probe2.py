import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng import legal
from ng.emulator import BizHawk
from ng.inputs import read_inputs
from ng.mode import TICKS

if __name__ == "__main__":
    ref = legal.TasRef()
    first, tas = ref.stage_rows(0)
    j = json.load(open("work/a12/effects_1-1.json"))
    res = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
    hist = read_inputs("logs/a12_intro.inputs.txt")
    a, b = int(sys.argv[1]), int(sys.argv[2])
    proj = legal.enforce(res, hist)
    with BizHawk(log_name="a12_probe2.log") as e:
        e.load("ref4751/00_1-1_control"); e.tick(TICKS)
        tr = legal.play(e, res[:b])          # resolved (rate not enforced)
        e.load("ref4751/00_1-1_control"); e.tick(TICKS)
        tr2 = legal.play(e, proj[:b])
    for i in range(a, b):
        r = ref.tr[first - 1 + i]
        print(f"{i:4d} {r['frame']} TAS {'+'.join(tas[i]):18s} x{r['x']:3d} y{r['y']:3d} sc{r['scroll']:3d} hp{r['hp']} | RES {'+'.join(res[i]):12s} x{tr[i]['x']:3d} y{tr[i]['y']:3d} sc{tr[i]['scroll']:3d} | PRJ {'+'.join(proj[i]):12s} x{tr2[i]['x']:3d} y{tr2[i]['y']:3d} sc{tr2[i]['scroll']:3d} hp{tr2[i]['hp']}")
