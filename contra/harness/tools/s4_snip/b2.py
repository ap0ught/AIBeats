# closed-loop boss fight (offline plan + executor) from a boss-room state; then the exit
import json, importlib, time
import multiprocessing as mp
import contra.stages.base_bsim as bs
import contra.stages.base_bplan as bp
import contra.stages.base_bfight as bf
import contra.stages.base_boss as bb
for mod in (bs, bp, bf):
    importlib.reload(mod)
ROOT = ""
stage, state, tag, out = G.get("B2", (4, "s4/boss", "p0", "x_fight_p0"))
rep = json.load(open(ROOT + f"logs/s{stage}/{tag}_report.json"))
rows0 = [tuple(r) for r in json.load(open(ROOT + f"logs/s{stage}/{tag}_rows.json"))][:rep["boss_load"]]
S = bc.Sess(e, hist=rows0[-40:], fields=bc.make_fields())
S.load(state)
S.rows = list(rows0)          # so that the press history at the boundary is the real one
bf.CACHE_DIR = ROOT + f"logs/s{stage}/x_plancache"
bf.LOG_FILE = ROOT + f"logs/s{stage}/{out}.log"
t = time.time()
with mp.get_context("spawn").Pool(6) as pool:
    fight = bf.BossFight(S, pool=pool, verbose=True)
    info = fight.run()
print({k: v for k, v in info.items() if k not in ("events",)})
print("events:", info["events"])
n_boss = len(S.rows) - len(rows0)
print("boss rows", n_boss, "ok", info.get("ok"), "secs", round(time.time() - t))
json.dump({"rows": S.rows, "boss_load": len(rows0), "boss_rows": n_boss, "info": {k: v for k, v in info.items()}},
          open(ROOT + f"logs/s{stage}/{out}_partial.json", "w"))
if info.get("ok"):
    e.save(f"s{stage}/x_boss_dead")
    x = bb.solve_exit(S)
    print("exit", x, "end", {k: S.s[k] for k in ("frame", "level", "lroutine", "weapon", "lives")}, "total rows", len(S.rows))
    json.dump({"rows": S.rows, "boss_load": len(rows0), "boss_rows": n_boss, "info": {k: v for k, v in info.items()}},
              open(ROOT + f"logs/s{stage}/{out}.json", "w"))
