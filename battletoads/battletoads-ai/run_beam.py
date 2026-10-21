"""python run_beam.py <name> <bookmark> <steps> <width>  -> logs/beam_<name>.json, states/beam_<name>_end"""
import json, sys, time
from toads.emulator import BizHawk, LOGS_DIR
from toads.beam import beam
from toads import tokens
name, bm, steps, width = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
emu = BizHawk(log_name=f"beam_{name}.log")
t0 = time.time()
best = beam(emu, bm, steps=steps, width=width, stop=lambda i: i["camera"] >= 97 and i["alive"] == 0)
(LOGS_DIR / f"beam_{name}.json").write_text(json.dumps({"bookmark": bm, "inputs": best.inputs, "info": best.info,
                                                        "score": best.score, "wall": time.time() - t0}))
emu.load(bm)
for b in best.inputs: emu.step(tuple(x for x in b.split("+") if x), 1)
emu.save(f"beam_{name}_end")
emu.close()
print("done", len(best.inputs), "frames", best.info, f"{time.time()-t0:.0f}s")
tokens.mark(f"beam {name}", {"frames": len(best.inputs), "info": best.info})
