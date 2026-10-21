"""Beam search over input macros. The brute force that can see.

From a bookmark, every STEP frames each state in the beam tries every macro (a direction combo, with or without a
punch or a jump on the first frames). Every child is scored from RAM alone; the WIDTH best survive. The game is
deterministic, so the survivor's input list replays exactly from the bookmark.

Scoring uses only what ramscan found (knowledge/ram.json and the notes in journal/):
    camera $87 (progress), lives $11, health = filled HUD squares $1C9-$1CE,
    enemies = object slots 14-18 with a nonzero Y ($40E+slot).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from .emulator import BizHawk

DIRS = [(), ("Right",), ("Left",), ("Up",), ("Down",), ("Right", "Up"), ("Right", "Down"), ("Left", "Up"),
        ("Left", "Down")]
# (direction, action): action "" hold, "B" punch, "A" jump, "dash" tap-release-tap run (192 speed per the TAS
# notes), "dashjump" A on the second tap, "ram" dash then B (headbutt at full run)
MACROS = [(d, "") for d in DIRS] + [(d, "B") for d in DIRS] + [(d, "A") for d in (("Right",), ("Left",), ())]
MACROS += [(d, a) for d in (("Right",), ("Left",), ("Right", "Up"), ("Right", "Down")) for a in ("dash", "dashjump")]
# "ram": the measured recipe for a one-hit headbutt: come to a COMPLETE stop, then tap-release-tap, hold 4, B.
# Launched while still moving it does 4 damage; from a standstill it does 15 (a pig's whole bar).
MACROS += [(d, "ram") for d in (("Right",), ("Left",), ("Right", "Up"), ("Right", "Down"), ("Left", "Up"), ("Left", "Down"))]
MACROS += [((), "stop"), ((), "finish")]

W = dict(camera=6.0, kill=400.0, dmg=25.0, alive=100.0, health=40.0, life=6000.0, near=0.4, x=1.5, level=100000.0, warp=8.0)

SLOTS = range(2, 15)


@dataclass
class Node:
    sid: str
    inputs: list = field(default_factory=list)
    score: float = 0.0
    info: dict = field(default_factory=dict)


def read_info(ram: bytes) -> dict:
    """Everything the score needs, read from the object table (feos's layout: 15 slots, stride 0xF)."""
    cam = ram[0x87] + 256 * ram[0x88]
    x = ram[0x3FD] + 256 * ((ram[0x3EE] + 128) % 256 - 128)
    hp = ram[0x51A]
    # real enemies only: not the warp portal (Anim_2 0x55, whose "HP" is its lifetime) and not the level-start
    # drop-in object (ID 6, HP 47, which dies on its own)
    foes = [(s, ram[0x51A + s]) for s in SLOTS
            if ram[0x3C1 + s] and ram[0x51A + s] and ram[0x583 + s] != 0x55 and ram[0x3C1 + s] & 0x7F != 6]
    tx, ty = ram[0x3FD], ram[0x41B]
    dist = min((abs(ram[0x3FD + s] - tx) + abs(ram[0x41B + s] - ty) for s, _ in foes), default=0)
    # a warp portal: object with Anim_2 == 0x55 (feos's object viewer). Distance in x (world), depth and height.
    wd = 0
    for s in SLOTS:
        if ram[0x583 + s] == 0x55 and ram[0x3C1 + s]:
            wx = ram[0x3FD + s] + 256 * ((ram[0x3EE + s] + 128) % 256 - 128)
            wd = abs(wx - x) + abs(ram[0x41B + s] - ty) + abs(ram[0x439 + s] - ram[0x439])
            break
    return dict(camera=cam, x=x, hp=hp, lives=ram[0x11], level=ram[0x10], alive=len(foes),
                foe_hp=sum(h for _, h in foes), dist=dist, spd=ram[0x565], warp=wd)


def score(info: dict, base: dict, kills: int) -> float:
    dmg = base.get("foe_hp0", 0) - info["foe_hp"]           # HP taken off enemies since the bookmark (kills included)
    lvl = W["level"] if info["level"] not in (base["level"], 0, 255) else 0.0
    return (W["camera"] * (info["camera"] - base["camera"]) + W["x"] * (info["x"] - base["x"]) + W["dmg"] * dmg
            + W["kill"] * kills - W["alive"] * info["alive"] + W["health"] * info["hp"]
            - W["life"] * (base["lives"] - info["lives"]) + lvl
            # while enemies stand, the screen is locked: what matters is getting to them. Once the arena is clear
            # (or there never was one) the portal distance takes over; a vanished portal counts as far away.
            - (W["near"] * 4 * info["dist"] if info["alive"] else 0)
            - (0 if info["alive"] else W["warp"] * (info["warp"] if info["warp"] else (base.get("warp0", 0) + 200))))


def run_macro(emu: BizHawk, macro, n: int) -> list:
    d, a = macro
    out = []

    def go(btn, k):
        if k > 0:
            emu.step(btn, k)
            out.extend(["+".join(btn)] * k)

    def stop(limit=45):
        for _ in range(limit):
            if emu.state().xspd == 0:
                return
            go((), 1)

    if a == "":
        go(d, n)
    elif a == "B":
        go(d + (a,), 2); go(d, n - 2)
    elif a == "A":                                               # A held: jump height scales with the hold (40 -> 75 px)
        go(d + (a,), max(2, n - 4)); go(d, 4)
    elif a == "stop":
        stop(n)
    elif a == "finish":
        # measured on a Level 3 rat: a headbutt knocks it down (~93 frames, untouchable). Stand 24-32 px away on
        # its line; a few frames after it stands, a second headbutt kills it outright.
        for _ in range(n * 4):
            r = emu.ram_all()
            tx, ty = r[0x3FD], r[0x41B]
            foes = [(s, r[0x3FD + s], r[0x41B + s], r[0x4B1 + s]) for s in SLOTS
                    if r[0x3C1 + s] and r[0x51A + s] and r[0x583 + s] != 0x55 and r[0x3C1 + s] & 0x7F != 6]
            if not foes:
                break
            fs, fx, fy, fst = min(foes, key=lambda f: abs(f[1] - tx) + abs(f[2] - ty))
            dx, dy = fx - tx, fy - ty
            side = ("Right",) if dx > 0 else ("Left",)
            if 20 <= abs(dx) <= 40 and abs(dy) <= 3:
                if fst != 64:
                    go((), 4); go(side, 1); go((), 1); go(side, 4); go(side + ("B",), 2); go(side, 6)
                    break
                go((), 1)
            else:
                h = side if abs(dx) > 40 else (("Left",) if dx > 0 else ("Right",)) if abs(dx) < 20 else ()
                go(h + (("Down",) if dy > 3 else ("Up",) if dy < -3 else ()), 1)
    else:
        h = tuple(b for b in d if b in ("Right", "Left"))
        v = tuple(b for b in d if b not in ("Right", "Left"))
        go(h + v, 1); go(v, 1)
        if a == "dash":
            go(d, n - 2)
        else:                                                    # dashjump: A on the second tap
            go(d + ("A",), max(2, n - 6)); go(d, 4)
    if len(out) < n:                 # every macro advances at least n frames, or a no-op child wins the time penalty
        go((), n - len(out))
    return out


def beam(emu: BizHawk, bookmark: str, steps: int = 60, width: int = 8, step: int = 16, stop=None, log=print):
    emu.load(bookmark)
    base = read_info(emu.ram_all())
    root = Node(emu.msave(), [], 0.0, base)
    root.info["kills"] = 0
    beam_nodes = [root]
    t0 = time.time()
    for k in range(steps):
        children = []
        for node in beam_nodes:
            for m in MACROS:
                emu.mload(node.sid)
                ins = run_macro(emu, m, step)
                info = read_info(emu.ram_all())
                kills = node.info["kills"] + max(0, node.info["alive"] - info["alive"])
                info["kills"] = kills
                children.append(Node("", node.inputs + ins, score(info, base, kills), info))
                children[-1]._parent = node          # re-run to get a state only for the survivors
                children[-1]._macro = m
        children.sort(key=lambda c: -c.score)
        keep, seen = [], set()
        for c in children:
            key = (c.info["camera"], c.info["alive"], c.info["health"], c.info["dist"] // 4)
            if key in seen:
                continue
            seen.add(key)
            keep.append(c)
            if len(keep) >= width:
                break
        for c in keep:                                # materialize survivor states
            emu.mload(c._parent.sid)
            run_macro(emu, c._macro, step)
            c.sid = emu.msave()
        for n in beam_nodes:
            emu.mfree(n.sid)
        beam_nodes = keep
        best = beam_nodes[0]
        log(f"  step {k + 1:3d}  frames {len(best.inputs):5d}  score {best.score:8.1f}  {json.dumps(best.info)}  "
            f"{time.time() - t0:.0f}s")
        if stop and stop(best.info):
            break
    return beam_nodes[0]
