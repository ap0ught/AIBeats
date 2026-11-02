"""ng.solve.items - every lantern of the game (ROM tables) + the owner's maps, and a ninpo / item planner.

Lantern data (bank07 $EA2E load_room, $D8D5 spawn_lanterns, $DB8A take_powerup; bank 2 tables):
  count  = bank0 $AE10[room]            (high bit = none)
  column = (bank2 $8700[2*room] pointer)[i]   -> world x = column * 16 (= the x of the icon on the owner's maps)
  y/item = (bank2 $8760[2*room] pointer)[i]   -> y = high nibble * 16 (RAM $4E1), item = low nibble (RAM $4C9)
  A lantern hangs when the screen's leading edge column reaches its column; rooms that never scroll never hang their
  lanterns (2-1's one-screen room has a health refill at column 3, 6-2's has a Windmill at column 3).
Item ids ($DBC9 pickup_kind): 0 ninpo+5, 1 ninpo+10, 2 1-UP, 3 health+6, 4 hourglass, 5 500 pts, 6 1000 pts,
  7 Invincible Fire-Wheel, 8 Throwing Star (3 ninpo/throw), 9 Windmill (5), 10 Art of the Fire Wheel (5),
  11 Jump & Slash (5 per spin). Ninpo caps at 99. Weapon items REPLACE the equipped weapon ($C9).

Maps: resources/maps/<stage>.png (Rick N. Bruns, NESMaps; extracted from Ninja_Gaiden_Maps_with_Items_0878eb81.zip).
For the one-row stages (208 px high) icon x = column * 16 exactly (checked by check_maps(): every ROM lantern has an
icon in the top strip of its map at x = 16 * column). Multi-room maps (2-1, 2-2&2-3, 4-1, 4-3, 5-2, 5-3, 6-2, 6-3)
stack the rooms; their index is the ROM list per room (index(): knowledge/maps_index.json).

    python -m ng.solve.items [stage ...]            print the lanterns per room (+ map check)
    plan(stage, ninpo_in, need_out, route=None)     which ninpo lanterns to break, cost in frames (see doc)
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from . import common as C

ITEM = {0: "ninpo+5", 1: "ninpo+10", 2: "1-UP", 3: "health", 4: "hourglass", 5: "500pts", 6: "1000pts",
        7: "InvFireWheel", 8: "Star", 9: "Windmill", 10: "FireWheel", 11: "J&S"}
WEAPON_ID = {7: 0x84, 8: 0x81, 9: 0x82, 10: 0x80, 11: 0x85}
WEAPON_COST = {0x81: 3, 0x82: 5, 0x80: 5, 0x85: 5, 0x84: 5}
NINPO = {0: 5, 1: 10}
MAP_FILE = {"1-1": "1-1", "2-1": "2-1", "2-2": "2-2 & 2-3", "2-3": "2-2 & 2-3", "3-1": "3-1", "3-2": "3-2",
            "4-1": "4-1", "4-2": "4-2", "4-3": "4-3", "5-1": "5-1", "5-2": "5-2", "5-3": "5-3", "6-1": "6-1",
            "6-2": "6-2", "6-3": "6-3"}
MAPS = C.PROJECT / "resources" / "maps"


@lru_cache(None)
def lanterns_rom() -> dict[int, list[dict]]:
    d = C.ROM.read_bytes()
    b0, b2 = 16, 16 + 2 * 0x4000

    def a2(a):
        return b2 + a - 0x8000

    out = {}
    for room in range(48):
        n = d[b0 + 0x2E10 + room]
        lst = []
        if not n & 0x80:
            pc = d[a2(0x8700) + 2 * room] | d[a2(0x8700) + 2 * room + 1] << 8
            py = d[a2(0x8760) + 2 * room] | d[a2(0x8760) + 2 * room + 1] << 8
            for i in range(n):
                col, v = d[a2(pc) + i], d[a2(py) + i]
                if col == 255:
                    continue
                lst.append({"room": room, "idx": i, "col": col, "x": col * 16, "y": v & 0xF0, "item": v & 15,
                            "name": ITEM.get(v & 15, "?")})
        out[room] = lst
    return out


def stage_lanterns(stage) -> list[dict]:
    out = []
    for r in C.rooms_of(stage):
        for ln in lanterns_rom()[r]:
            out.append(dict(ln, stage=C.NAMES[C.stage_index(stage)]))
    return out


def check_maps() -> dict:
    """For one-row maps: is there an icon (non-black, non-sky pixel cluster) in the top strip at x = 16*col?"""
    from PIL import Image
    res = {}
    for st, fn in MAP_FILE.items():
        p = MAPS / f"{fn}.png"
        if not p.exists():
            continue
        im = Image.open(p).convert("RGB")
        W, H = im.size
        if H != 208:
            res[st] = "multi-room map (rooms stacked; not auto-checked)"
            continue
        px = im.load()
        ok = bad = 0
        for ln in stage_lanterns(st):
            hit = 0
            for x in range(ln["x"], min(W, ln["x"] + 16)):
                for y in range(0, 26):
                    r, g, b = px[x, y]
                    if r + g + b > 120:
                        hit += 1
            if hit >= 6:
                ok += 1
            else:
                bad += 1
        res[st] = f"{ok} icons found / {ok + bad} ROM lanterns"
    return res


def index(write=True) -> dict:
    idx = {"_about": "Lanterns per stage/room from the ROM tables (ng/solve/items.py); x = world x in the room "
                     "(= icon x on the owner's map resources/maps/<map>.png), y = RAM $4E1 (feet line of the lantern).",
           "maps_check": check_maps(), "stages": {}}
    for i, n in enumerate(C.NAMES):
        rooms = {}
        for r in C.rooms_of(i):
            rooms[str(r)] = [{k: v for k, v in ln.items() if k in ("col", "x", "y", "item", "name")}
                             for ln in lanterns_rom()[r]]
        idx["stages"][n] = {"map": MAP_FILE.get(n), "rooms": rooms,
                            "ninpo_total": sum(NINPO.get(ln["item"], 0) for ln in stage_lanterns(i))}
    if write:
        (C.KNOW / "maps_index.json").write_text(json.dumps(idx, indent=1), encoding="utf-8")
    return idx


# ------------------------------------------------------------------------------------------------ planner
def route_from_trace(trace) -> list[tuple]:
    """[(frame, room, X, y)] from a list of trace dicts (ng State dicts or TAS trace rows)."""
    out = []
    for s in trace:
        if s is None:
            continue
        out.append((s.get("frame"), s.get("room"), C.abs_x(s), s.get("y")))
    return out


def tas_route(stage) -> list[tuple]:
    import a56_common as A
    tr = A.tas_trace()
    i = C.stage_index(stage)
    f0 = C.tas_control(i)
    f1 = C.tas_control(i + 1) if i < 21 else 39525
    return [(f, tr[f]["room"], C.abs_x(tr[f]), tr[f]["y"]) for f in range(f0, min(f1, len(tr)))]


def lantern_cost(ln, route) -> dict:
    """Frames a route must spend to break `ln` and catch its item (rough, optimistic):
    the route's closest point (same room) to the slash spot; 0-2 f if the route already passes within the sword's
    reach (32 px ahead, 16 px vertically around feet-8), else a detour 2 * dx / 1.5 + climb / 2.4 (+ 4 for the item
    to fall and be caught when it drops away from the route)."""
    best = None
    for f, room, X, y in route:
        if room != ln["room"]:
            continue
        dx = abs(X - ln["x"])
        dy = abs((y - 8) - ln["y"])
        reach_dx = max(0, dx - 30)
        reach_dy = max(0, dy - 14)
        c = (2 * reach_dx / 1.5) + (reach_dy / 2.4 if (y - 8) > ln["y"] else reach_dy / 4.0)
        if best is None or c < best[0]:
            best = (c, f, X, y)
    if best is None:
        return {"cost": None, "why": "route never in this room"}
    c, f, X, y = best
    cost = 1.0 if c == 0 else c + 4
    return {"cost": round(cost, 1), "frame": f, "at": (X, y)}


def plan(stage_list, ninpo_in=0, needs=None, route=None, weapon=None) -> dict:
    """Ninpo plan over consecutive stages.
    stage_list: e.g. ["3-1", "3-2", "3-3"]; needs: {stage: ninpo needed at that stage's control (boss)} or
    {stage: ("spend", n)} for throws planned inside a stage. route: {stage: [(frame, room, X, y)]} (default the
    TAS's line). weapon: the weapon to keep (weapon lanterns of other kinds are flagged AVOID: picking them up
    replaces it). Returns the cheapest lantern set (greedy by cost per ninpo, cost 1 f = on the route) that meets
    every need in order, the expected ninpo at every stage start, and the weapon lanterns met on the route."""
    needs = needs or {}
    cand = []
    for st in stage_list:
        r = (route or {}).get(st) or tas_route(st)
        for ln in stage_lanterns(st):
            lc = lantern_cost(ln, r)
            cand.append(dict(ln, **lc))
    ninpo_l = [c for c in cand if c["item"] in NINPO and c["cost"] is not None]
    weap = [c for c in cand if c["item"] in WEAPON_ID]
    chosen = []
    np_ = ninpo_in
    order = list(stage_list)
    for st in order:
        need = needs.get(st)
        if need is None:
            continue
        spend = 0
        if isinstance(need, tuple):
            spend = need[1]
            need = need[1]
        # lanterns available before this stage's control (earlier stages) or inside it when spending in-stage
        upto = order[:order.index(st) + (1 if spend else 0)]
        pool = sorted([c for c in ninpo_l if c["stage"] in upto and c not in chosen],
                      key=lambda c: c["cost"] / NINPO[c["item"]])
        have = ninpo_in + sum(NINPO[c["item"]] for c in chosen) - sum(
            (v[1] if isinstance(v, tuple) else 0) for k, v in needs.items() if order.index(k) < order.index(st))
        while have < need and pool:
            c = pool.pop(0)
            chosen.append(c)
            have += NINPO[c["item"]]
        np_ = have
    keep = []
    for w in weap:
        wid = WEAPON_ID[w["item"]]
        keep.append(dict(w, verdict="TAKE" if (weapon is None or wid == weapon) else "AVOID (replaces weapon)"))
    return {"chosen": sorted(chosen, key=lambda c: (c["stage"], c["room"], c["x"])),
            "cost_frames": round(sum(c["cost"] for c in chosen), 1), "ninpo_after": np_,
            "weapons_on_route": keep, "all_ninpo_lanterns": ninpo_l}


def _main(argv):
    idx = index(write=True)
    print("maps:", json.dumps(idx["maps_check"], indent=1))
    sts = argv or C.NAMES
    for st in sts:
        print(f"== {st}  (ninpo total {idx['stages'][st]['ninpo_total']}, map {MAP_FILE.get(st)})")
        for ln in stage_lanterns(st):
            print(f"   room {ln['room']:2d} col {ln['col']:3d} x {ln['x']:4d} y {ln['y']:3d}  {ln['name']}")


if __name__ == "__main__":
    import sys
    _main(sys.argv[1:])
