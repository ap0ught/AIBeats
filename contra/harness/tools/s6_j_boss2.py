"""Job (side job, stage 6 boss): the first builder's boss beam from the best segment's b_last checkpoint
(s6/final_ph66_b_last, row 2873; its fight ended at row 3434 = 561 rows later) with wider beams."""
import time
from contra.stages import s6
from contra.stages.s6run import Proc, Mark

for width in (32,):
    f0 = sim.load("s6/final_ph66_b_last")
    r = s6.make_runner(sim, route=[Mark("boss_in"), Proc(s6.boss_proc, "boss"), Mark("boss_dead")], name=f"s6w{width}")
    r.user["boss_width"] = width
    t0 = time.time()
    res = r.solve(max_deaths=5)
    c = r.c
    b0 = next((i for i, f in enumerate(c.tr) if s6.boss_of(f) is not None), None)
    print("width", width, res, "rows to the kill", len(c.rows), "(first builder: 561)", "boss created at row", b0,
          "kill", len(c.rows) - (b0 or 0), "frames after creation (first builder: 141)", "seconds", round(time.time() - t0),
          flush=True)
