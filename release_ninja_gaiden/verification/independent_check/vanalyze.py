"""Analyse a vreplay.lua run (verifier's own code; no project imports).

  python vanalyze.py <outname> [--json out.json]

Events (row k = the input row applied on emulator framecount k, .bk2 numbering; picture of row k = screenshot
taken right after frame k):
  START_ram  first row with $33 == $97 and $6D == 0 (the frame control is gained, per the autosplitter)
  START_seen first row whose PICTURE shows Ryu (screenshot diff in the playfield vs the previous row + OAM count)
  END_ram    first row in 6-5 ($6D == 21) with timer $63 == 0 after the demon's tally began
  END_seen   first row whose PICTURE shows TIMER-000 (the three HUD timer digit cells are pixel-identical '0'
             glyphs; only checked while $6D == 21 and $63 <= 4, where every frame has a screenshot)
  T_s        per stage: first row whose nametable holds valid timer digits after the stage load (+ picture offset
             measured at 1-1 and at END from the screenshots)
time = (END_seen - START_seen) / 60.0988 s
"""
import csv, glob, hashlib, json, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 60.0988
STAGES = ["1-1", "1-2", "2-1", "2-2", "2-3", "3-1", "3-2", "3-3", "4-1", "4-2", "4-3", "4-4", "5-1", "5-2", "5-3",
          "5-4", "6-1", "6-2", "6-3", "6-4a", "6-4b", "6-5"]


def load(name):
    d = os.path.join(HERE, "run", name)
    rows = []
    with open(os.path.join(d, "frames.csv")) as f:
        for r in csv.DictReader(f):
            rows.append(r)
    for r in rows:
        for k in list(r):
            if k not in ("tdig", "pal"):
                r[k] = int(r[k])
    meta = {}
    for line in open(os.path.join(d, "meta.txt"), encoding="utf-8"):
        if "=" in line:
            k, v = line.rstrip("\n").split("=", 1)
            meta[k] = v
        elif line.strip():
            meta[line.strip()] = True        # DONE, "ERROR ...", "BAD_TOKEN ..." lines
    return d, rows, meta


def shot(d, row):
    p = os.path.join(d, "shots", f"s{row:06d}.png")
    if not os.path.exists(p):
        return None
    return np.asarray(Image.open(p).convert("RGB")).astype(np.int16)


def digit_cells(img):
    h = img.shape[0]
    y0 = 32 if h >= 240 else 24          # the TIMER digits (PPU $20A9-$20AB) as drawn: lines 24-31 of the 224-line
                                         # screenshot (measured: the 001 -> 000 change, TAS replay row 39,530)
    return [img[y0:y0 + 8, x:x + 8] for x in (72, 80, 88)]


def analyse(name):
    d, R, meta = load(name)
    byrow = {r["row"]: r for r in R}
    out = {"name": name, "meta": {k: v for k, v in meta.items() if not k.startswith("ram")}}
    for k in ("ram_at_last_row", "ram_after_last"):
        if k in meta:
            out[k + "_sha1"] = hashlib.sha1(bytes.fromhex(meta[k])).hexdigest()
    # ---- START
    st_ram = next((r["row"] for r in R if r["r33"] == 0x97 and r["r6D"] == 0), None)
    out["start_ram"] = st_ram
    st_seen, diffs = None, {}
    if st_ram:
        for k in range(st_ram - 3, st_ram + 6):
            a, b = shot(d, k), shot(d, k - 1)
            if a is None or b is None:
                continue
            h = a.shape[0]
            dd = float(np.abs(a[h // 4:, :] - b[h // 4:, :]).mean())
            diffs[k] = (round(dd, 2), byrow[k]["nspr"])
        for k in sorted(diffs):
            if k >= st_ram and diffs[k][0] > 0.5:
                st_seen = k
                break
    out["start_seen"] = st_seen
    # picture check of the HUD digit cells at 1-1: first screenshot with all three cells lit (vs nametable)
    out["start_digits_picture"] = None
    for k in range((st_ram or 170) - 3, (st_ram or 170) + 12):
        a = shot(d, k)
        if a is not None and min(float(x.mean()) for x in digit_cells(a)) > 10:
            out["start_digits_picture"] = k
            break
    out["start_diffs"] = diffs
    # ---- digit tile map: rows with a stable timer for 8 rows; nametable tiles == digits of $63
    votes = {}
    i_start = next((i for i, r in enumerate(R) if r["row"] == st_ram), 0)
    for i in range(i_start + 8, len(R)):
        r = R[i]
        if r["r6D"] > 21 or not all(R[j]["r63"] == r["r63"] for j in range(i - 7, i + 1)) or r["r63"] > 150:
            continue
        s = f"{r['r63']:03d}"
        t = r["tdig"]
        for c in range(3):
            votes.setdefault(t[2 * c:2 * c + 2], {}).setdefault(s[c], 0)
            votes[t[2 * c:2 * c + 2]][s[c]] += 1
    tile2dig = {}
    for t, v in votes.items():
        dgt, n = max(v.items(), key=lambda x: x[1])
        if n >= 20 and n >= 0.95 * sum(v.values()):
            tile2dig[t] = dgt
    out["tile2dig"] = tile2dig

    out["tile_is_digit"] = all(t == "%02X" % int(v) for t, v in tile2dig.items())

    def dec(t):
        # HUD digit tiles are the digit values 00..09 (checked by the votes above: tile_is_digit)
        b = [int(t[2 * c:2 * c + 2], 16) for c in range(3)]
        return b[0] * 100 + b[1] * 10 + b[2] if all(x <= 9 for x in b) else None
    # ---- stages: load = first row with the new $6D; timer start = first row after load where $62 changes
    stages, cur = [], None
    for i, r in enumerate(R):
        if r["r6D"] <= 21 and r["r6D"] != cur and (cur is None or r["r6D"] == cur + 1):
            cur = r["r6D"]
            stages.append({"stage": STAGES[cur], "load": r["row"] if cur else None, "i": i})
    for k, s in enumerate(stages):
        i0 = s.pop("i")
        i0 = i0 if k else i_start
        i1 = len(R)
        if k + 1 < len(stages):
            i1 = next(j for j in range(len(R)) if R[j]["row"] == (stages[k + 1]["load"]))
        tr = next((R[j]["row"] for j in range(i0 + 1, i1) if R[j]["r62"] != R[j - 1]["r62"]), None)
        s["timer_runs"] = tr       # first row whose RAM shows the sub-timer moving
        s["digits_nt"] = next((R[j]["row"] for j in range(i0, i1) if dec(R[j]["tdig"]) is not None
                               and (j == 0 or dec(R[j - 1]["tdig"]) is None)), None)
        s["rooms"] = sorted({R[j]["r6E"] for j in range(i0, i1)})
        s["hp_min"] = min(R[j]["r65"] for j in range(i0, i1))
        s["lives_min"] = min(R[j]["r76"] for j in range(i0, i1))
    out["stages"] = stages
    # rooms: first row of every new $6E value
    rooms, prev = [], None
    for r in R:
        if r["r6E"] != prev and r["r6E"] < 64:
            rooms.append((r["row"], r["r6E"]))
            prev = r["r6E"]
    out["rooms"] = rooms
    lives0 = R[min(len(R) - 1, 400)]["r76"]
    out["lives_drop_rows"] = [R[i]["row"] for i in range(1, len(R)) if R[i]["r76"] < R[i - 1]["r76"] and R[i]["row"] > 400]
    out["lag_rows"] = sum(r["lagged"] for r in R)
    # ---- END
    end_ram = next((r["row"] for r in R if r["r6D"] == 21 and r["r63"] == 0 and r["r66"] == 0), None)
    out["end_ram"] = end_ram
    end_seen, cells = None, {}
    for r in R:
        if r["r6D"] == 21 and r["r63"] <= 4:
            a = shot(d, r["row"])
            if a is None:
                continue
            c = digit_cells(a)
            lit = [float(x.mean()) for x in c]
            same = bool(np.array_equal(c[0], c[1]) and np.array_equal(c[1], c[2]))
            cells[r["row"]] = {"r63": r["r63"], "nt": r["tdig"], "nt_dec": dec(r["tdig"]), "lit": [round(x) for x in lit], "000": same and min(lit) > 10}
            if end_seen is None and same and min(lit) > 10 and r["row"] >= (end_ram or 0):
                end_seen = r["row"]
    out["end_seen"] = end_seen
    out["end_cells"] = cells
    out["end_nt"] = next((r["row"] for r in R if r["r6D"] == 21 and r["r63"] == 0 and dec(r["tdig"]) == 0), None)
    if st_seen and end_seen:
        fr = end_seen - st_seen
        out["frames"] = fr
        out["seconds"] = fr / FPS
        out["time"] = f"{int(out['seconds'] // 60)}:{out['seconds'] % 60:06.3f}"
    return out


if __name__ == "__main__":
    o = analyse(sys.argv[1])
    if "--json" in sys.argv:
        json.dump(o, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    for k in ("meta", "ram_at_last_row_sha1", "ram_after_last_sha1", "start_ram", "start_seen", "start_diffs",
              "tile2dig", "end_ram", "end_nt", "end_seen", "frames", "seconds", "time", "lives_drop_rows", "lag_rows"):
        print(k, o.get(k))
    for s in o["stages"]:
        print(" ", s)
