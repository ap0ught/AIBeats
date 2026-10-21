import sys, time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s5_ufo_sim import plan

ACC = [(22, 164), (31, 131), (146, 13), (63, 201), (71, 210), (46, 185), (217, 170), (87, 189), (48, 35), (7, 163)]

def job(a):
    lead, x, width, gap = a
    res = plan(60, 164 * 256 + 0x2a, x, ACC, 102, 128, 48, 102 - lead, width=width, rejump_gap=gap)
    return a, None if res is None else res[0] - 102

if __name__ == "__main__":
    width = int(sys.argv[1])
    jobs = [(lead, x, width, gap) for x in (128, 125) for gap in (0,) for lead in range(12, 62, 2)]
    t0 = time.time()
    with ProcessPoolExecutor(6) as ex:
        out = list(ex.map(job, jobs))
    for x in (128, 125):
        print("x", x, " ".join(f"{a[0]}:{r}" for a, r in out if a[1] == x))
    print(f"{time.time() - t0:.0f} s")
