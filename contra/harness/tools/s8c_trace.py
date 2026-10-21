"""Per-row trace of a finished stage 8 segment + what every B press fired (read-only replay, no pokes).

    python tools/s8c_trace.py <state> <seg name under logs/, no extension> [<out json under logs/>]

For every new B press: the row, how many pellets it created (0 = wasted: no bullet slot was free), Bill's
position, the boss HP. Summary per section (P1 run, guardian fight, P3 run, heart fight, ending).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, TR  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR  # noqa: E402

GUARDIAN, HEART = 0x10, 0x16


def fields():
    f = dict(TR)
    for s in range(10):
        f[f"br{s}"] = 0x438 + s
    return f


def slot(s, typ):
    for k in range(16):
        if s[f"r{k}"] and s[f"t{k}"] == typ:
            return k
    return None


def births(tr):
    """births[k] = number of pellets created on trace index k."""
    out = [0] * len(tr)
    for k in range(1, len(tr)):
        a, p = tr[k], tr[k - 1]
        n = 0
        for s in range(10):
            if a[f"b{s}"] and (not p[f"b{s}"] or (p[f"br{s}"] >= 2 and a[f"br{s}"] < 2)):
                n += 1
        out[k] = n
    return out


def analyse(rows, tr, log=print):
    n = len(rows)
    bs = [i for i, r in enumerate(rows) if "B" in r and (i == 0 or "B" not in rows[i - 1])]
    bi = births(tr)
    ev = {}
    ev["spawn"] = next((k for k, s in enumerate(tr) if slot(s, GUARDIAN) is not None), None)
    ev["g_dead"] = next((k for k, s in enumerate(tr) if k > (ev["spawn"] or 0) and slot(s, GUARDIAN) is not None
                         and s[f"h{slot(s, GUARDIAN)}"] == 0), None)
    ev["scroll"] = next((k for k, s in enumerate(tr) if s["auto0"] > 0 and k > (ev["g_dead"] or 0)), None)
    ev["flag"] = next((k for k, s in enumerate(tr) if s["bossdef"] == 1), None)
    ev["A"] = next((k for k, s in enumerate(tr) if s["lroutine"] == 9), None)
    per = []
    used = set()
    for i in bs:
        # the pellets appear on the frame the game first sees the press (i, or i + 1 when the pad was ignored)
        k = next((q for q in (i, i + 1, i + 2) if q < len(tr) and bi[q] and q not in used), None)
        nb = 0
        if k is not None:
            used.add(k)
            nb = bi[k]
        per.append((i, nb))
    lag = [k for k, s in enumerate(tr[:n]) if s["lagged"]]
    secs = []
    if ev["spawn"] is not None and ev["g_dead"] is not None and ev["scroll"] is not None and ev["flag"] is not None:
        secs = [("P1 run", 0, ev["spawn"] - 80), ("guardian fight", ev["spawn"] - 80, ev["g_dead"] + 1),
                ("P3 run", ev["g_dead"] + 1, ev["scroll"] - 80), ("heart fight", ev["scroll"] - 80, ev["flag"] + 1),
                ("ending", ev["flag"] + 1, n)]
    out = {"events": ev, "lag_rows": lag, "sections": {}, "presses": per}
    log(f"events {ev}; B presses {len(bs)}; lag rows {lag}")
    for name, a, b in secs:
        ps = [(i, nb) for i, nb in per if a <= i < b]
        hist = [sum(1 for _, nb in ps if nb == q) for q in range(6)]
        d = {"rows": [a, b], "presses": len(ps), "pellets": sum(nb for _, nb in ps), "by_pellets_0_to_5": hist,
             "lag": sum(1 for k in lag if a <= k < b)}
        out["sections"][name] = d
        log(f"  {name:15s} rows {a:5d}..{b:5d} ({b - a:4d}): presses {len(ps):3d}, pellets {d['pellets']:3d}, "
            f"presses firing 0/1/2/3/4/5 pellets {hist}, lag {d['lag']}")
    return out


if __name__ == "__main__":
    state, name = sys.argv[1], sys.argv[2]
    outn = sys.argv[3] if len(sys.argv) > 3 else None
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / f"{name}.seg.json").read_text())["rows"]]
    with Engine(1, tag="s8", fields=fields()) as eng:
        tr = eng.sim(eng.root(state), rows + [()] * 3)
    res = analyse(rows, tr)
    if outn:
        p = LOGS_DIR / outn
        p.parent.mkdir(parents=True, exist_ok=True)
        keep = ("frame", "lagged", "x", "y", "screen", "scroll", "jump", "barrier", "rng", "fc")
        slim = []
        for k, s in enumerate(tr):
            d = {q: s[q] for q in keep}
            d["en"] = [(e, s[f"t{e}"], s[f"h{e}"], s[f"ex{e}"], s[f"ey{e}"]) for e in range(16) if s[f"r{e}"]]
            d["nb"] = sum(1 for q in range(10) if s[f"b{q}"])
            slim.append(d)
        res["trace"] = slim
        res["rows"] = ["+".join(r) for r in rows]
        p.write_text(json.dumps(res), encoding="utf-8")
        print("written", p)
