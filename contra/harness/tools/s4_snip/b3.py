# debug: why did the re-plan after the lost pad read at boss row 153 find nothing?
import json, importlib, time, pickle
import contra.stages.base_bsim as bs
import contra.stages.base_bplan as bp
import contra.stages.base_bfight as bf
for mod in (bs, bp, bf):
    importlib.reload(mod)
ROOT = ""
bf.CACHE_DIR = ROOT + "logs/s4/x_plancache"
rep = json.load(open(ROOT + "logs/s4/p0_report.json"))
rows0 = [tuple(r) for r in json.load(open(ROOT + "logs/s4/p0_rows.json"))][:rep["boss_load"]]
S = bc.Sess(e, hist=rows0[-40:], fields=bc.make_fields())
S.load("s4/boss")
S.rows = list(rows0)
n0 = len(rows0)
for _ in range(9):
    S.step(())
m = S.e.ram_all()
import multiprocessing as mp
with mp.get_context("spawn").Pool(6) as pool:
    best, res = bf.plan_portfolio(pool, m, bp.pad_from_rows(S.rows), 0, bf.PORTFOLIO_A)
acts = best["acts"]
print("plan", best["n"])
sim = bs.Sim.from_ram(m)
for i, a in enumerate(acts[:143]):
    row = bp.act_row(a)
    S.step(row)
    mm = S.e.ram_all()
    sim.step(mm[0xF1] & 15, 1 if mm[0xF5] & 0x80 else 0, 1 if mm[0xF5] & 0x40 else 0)
print("rows", len(S.rows) - n0, "last rows", S.rows[-6:], "next acts", [bp.act_row(a) for a in acts[143:150]])
m0 = S.e.ram_all()
sim0 = bs.Sim.from_ram(m0)
print("match", bf.model_matches(sim, m0), sim0.describe())
pad0 = bp.pad_from_rows(S.rows)
print("pad0", [bp.PSTATES[x] for x in pad0])
prev_act = bp.act_of_row(S.rows[-1])
print("prev_act", prev_act, bp.act_row(prev_act), [bp.PNEXT[pad0[k]][prev_act >> k & 1] for k in range(5)])
pl = bf.make_planner(sim0, "A", bf.PORTFOLIO_A[0], repeat=(0,))
bs.HZ_MARGIN = 1
dpad, a_new, b_new, np_ = bp.sim_inputs(pad0, prev_act)
s = sim0.copy(); s.step(dpad, a_new, b_new)
print("after repeat: dead", s.dead, "hz", [(h[0] >> 8, h[1] >> 8) for h in s.hz], "P", s.px, s.py, s.jump)
print("actions at next", [bp.act_row(a) for a in pl.actions(s, np_)])
pickle.dump({"m0": bytes(m0), "pad0": pad0, "prev_act": prev_act, "acts": acts}, open(ROOT + "logs/s4/x_dbg_b3.pkl", "wb"))
