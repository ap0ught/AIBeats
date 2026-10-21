# in parallel: stage 4 boss with the helmet search (E[0]) and stage 2 boss beam variants (E[1], E[2])
import json
import contra.stages.base_boss as bb
import contra.stages.base_boss4 as b4
import contra.stages.s2 as s2

rows4 = [tuple(r) for r in json.load(open("logs/s4/p0_rows.json"))][:json.load(open("logs/s4/p0_report.json"))["boss_load"]]
rows2 = [tuple(r) for r in json.load(open("logs/s2/p0_rows.json"))][:json.load(open("logs/s2/p0_report.json"))["boss_load"]]


def job(emu, j):
    kind = j[0]
    if kind == 4:
        S = bc.Sess(emu, hist=rows4[-40:], fields=bc.make_fields())
        S.load("s4/boss")
        info = b4.solve_boss(S, width=12, hold=4, try_glitch=j[1])
        rows0 = rows4
    else:
        S = bc.Sess(emu, hist=rows2[-40:], fields=bc.make_fields())
        S.load("s2/boss")
        info = bb.solve_boss(S, width=j[1], hold=j[2], max_layers=int(640 / j[2]), **s2.BOSS)
        rows0 = rows2
    res = {"job": j, "boss": info}
    if info.get("ok"):
        res["boss_dead"] = len(rows0) + len(S.rows)
        x = bb.solve_exit(S)
        res["exit"] = x
        res["end"] = {k: S.s[k] for k in ("frame", "level", "lroutine", "weapon", "lives")}
        res["total"] = len(rows0) + len(S.rows)
        json.dump(rows0 + list(S.rows), open(f"logs/s{kind}/boss_{'_'.join(map(str, j))}_rows.json", "w"))
    return res


for r in bc.pmap(E, job, G.get("B9JOBS", [(4, 2), (2, 20, 4), (2, 16, 3)])):
    print(r if "error" not in r else r["error"][-700:])
