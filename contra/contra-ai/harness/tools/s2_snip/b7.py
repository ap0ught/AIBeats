# boss beam, three parameter sets in parallel (one per emulator), from a disk state of the boss room's first frame
import json
import contra.stages.base_boss as bb
import contra.stages.s2 as s2
import contra.stages.s4 as s4

stage = G.get("BSTAGE", 4)
name = f"s{stage}"
boss = s4.BOSS if stage == 4 else s2.BOSS
tag = G.get("BTAG", "v0")
rows0 = [tuple(r) for r in json.load(open(f"logs/{name}/{tag}_rows_to_boss.json"))]
variants = G.get("BVAR", [(14, 4), (12, 3), (10, 5)])


def job(emu, var):
    width, hold = var
    S = bc.Sess(emu, hist=rows0[-40:], fields=bc.make_fields())
    S.load(f"{name}/{tag}_boss")
    b = bb.solve_boss(S, width=width, hold=hold, max_layers=int(700 / hold), **boss)
    res = {"var": var, "boss": b, "rows": list(S.rows)}
    if b["ok"]:
        x = bb.solve_exit(S)
        res["exit"] = x
        res["rows"] = list(S.rows)
        res["end"] = {k: S.s[k] for k in ("frame", "level", "lroutine", "weapon", "lives")}
    return res


out = bc.pmap(E, job, variants)
best = None
for r in out:
    print(r["var"], r["boss"], r.get("exit"), r.get("end"))
    if r["boss"]["ok"] and r.get("exit", {}).get("ok") and (best is None or len(r["rows"]) < len(best["rows"])):
        best = r
if best:
    full = rows0 + best["rows"]
    json.dump(full, open(f"logs/{name}/{tag}b_rows.json", "w"))
    print("best", best["var"], "boss frames", best["boss"]["frames"], "stage frames", len(full))
