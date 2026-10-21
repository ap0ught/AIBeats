"""Ending variance (track END, 2026-10-09): replay every stored Dark Queen fight (logs/pbeam_L13*.json) from its entry
bookmark, capture RAM per frame from the 19th hit to the T. Bird cut, and tabulate what the tail depends on.

    python end_var.py [seg ...]        -> logs/fix/endcap_<seg>.bin/.json, logs/fix/end_var.tsv
"""
import glob
import json
import os
import sys

from toads.emulator import BizHawk, LOGS_DIR, STATES_DIR

FIX = LOGS_DIR / "fix"
FIX.mkdir(exist_ok=True)
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
QID, DEAD = 0x7E, 0x46


def qslot(m):
    for s in range(2, 15):
        if m[0x3C1 + s] in (QID, DEAD):
            return s
    return None


def run(e, tag, bookmark, ins, skip="alt"):
    e.load(bookmark)
    rows = []
    f = 0
    prev = 13
    cut1 = back = cut2 = None
    extra = 0
    while True:
        if f < len(ins) and cut1 is None:
            b = bt(ins[f])
        elif cut1 is not None and back is None:
            b = ("A",) if (f - cut1) % 2 == 0 else ()
        else:
            b = ()
        e.step(b, 1)
        f += 1
        m = e.ram_all()
        rows.append(m)
        lv = m[0x10]
        if cut1 is None and prev == 13 and lv == 254:
            cut1 = f
        elif cut1 is not None and back is None and lv == 13:
            back = f
        elif back is not None and cut2 is None and prev == 13 and lv == 254:
            cut2 = f
        prev = lv
        if cut2 is not None:
            extra += 1
            if extra > 5:
                break
        if f > len(ins) + 3000 or (cut1 is None and lv not in (13, 254, 255, 0) and f > 300):
            break
    return summarize(tag, rows, cut1, back, cut2, bookmark)


def summarize(tag, rows, cut1, back, cut2, bookmark=""):
    hit20 = hit21 = resp = None
    d = {}
    for i in range(1, len(rows)):
        m, p = rows[i], rows[i - 1]
        f = i + 1
        if hit20 is None and m[0x586] == 240 and p[0x586] != 240:
            hit20 = f
        s = qslot(p)
        if hit21 is None and s is not None and p[0x3C1 + s] == QID and m[0x3C1 + s] == DEAD:
            hit21 = f
            d = {"slot": s, "qx": p[0x3FD + s], "qxh": p[0x3EE + s], "qh": p[0x439 + s], "qhh": p[0x42A + s], "qdepth": p[0x493 + s],
                 "qvel": m[0x4C0 + s], "qvlo": m[0x4CF + s], "qhp": p[0x51A + s], "t0b": m[0x0B], "t0c": m[0x0C],
                 "tx": m[0x3FD], "th": m[0x439], "tanim": m[0x3B5], "qstate": p[0x4B1 + s], "q4a2": p[0x4A2 + s]}
        if hit21 is not None and resp is None and s is not None and p[0x3C1 + s] == DEAD and m[0x3C1 + s] == QID:
            resp = f
            d["ctr_resp"] = m[0x586]
            d["t0b_resp"] = m[0x0B]
    first = max(0, (hit20 or 1) - 200)
    with open(FIX / f"endcap_{tag}.bin", "wb") as fh:
        for m in rows[first:]:
            fh.write(m)
    out = {"tag": tag, "bookmark": bookmark, "first_frame": first + 1, "frames": len(rows) - first, "hit20": hit20, "hit21": hit21,
           "resp": resp, "cut1": cut1, "back": back, "cut2": cut2, **d}
    (FIX / f"endcap_{tag}.json").write_text(json.dumps(out))
    return out


if __name__ == "__main__":
    segs = sys.argv[1:] or sorted(os.path.basename(p)[6:-5] for p in glob.glob(str(LOGS_DIR / "pbeam_L13*.json")))
    e = BizHawk(log_name="end_var.log")
    res = []
    for tag in segs:
        j = json.loads((LOGS_DIR / f"pbeam_{tag}.json").read_text())
        bm = j.get("bookmark")
        if not bm or not (STATES_DIR / f"{bm}.State").exists() or "partial" in tag or tag == "L13fast":
            continue
        try:
            r = run(e, tag, bm, j["inputs"])
        except Exception as ex:
            print(tag, "failed:", ex, flush=True)
            continue
        res.append(r)
        g = lambda k: r.get(k)
        tail = (g("cut2") - g("hit21")) if g("cut2") and g("hit21") else None
        print(tag, "hit20", g("hit20"), "hit21", g("hit21"), "resp", g("resp"), "cut1", g("cut1"), "back", g("back"), "cut2", g("cut2"),
              "| flight", (g("resp") - g("hit21")) if g("resp") and g("hit21") else None,
              "resp->cut1", (g("cut1") - g("resp")) if g("resp") and g("cut1") else None,
              "tower", (g("cut2") - g("back")) if g("cut2") and g("back") else None, "TAIL", tail,
              "| qh", g("qh"), g("qhh"), "qx", g("qx"), "vel", g("qvel"), g("qvlo"), "t0b", g("t0b"), "ctr_resp", g("ctr_resp"), flush=True)
    e.close()
    keys = sorted({k for r in res for k in r})
    (FIX / "end_var.tsv").write_text("\t".join(keys) + "\n" + "\n".join("\t".join(str(r.get(k, "")) for k in keys) for r in res) + "\n")
