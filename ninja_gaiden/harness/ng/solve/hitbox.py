"""ng.solve.hitbox - Ryu / sword / enemy / lantern / thrown-weapon boxes from RAM, ported from the two community Lua
scripts (resources/lua_hitbox_viewer/"NG1 - Hitbox Viewer.lua", resources/lua_hitboxes_detail/"NG1 - Hitboxes +
Platform boxes.lua") and CHECKED against the disassembly dl/NinjaGaidenNES/prg/bank07.asm. Where the two disagree the
ROM code wins and the Lua's version is noted.

RAM (bank07 labels):  Ryu x $86 (screen), y "height" $8A (feet), body height $90, sword reach up/down $91/$92,
  ryu_flags $84 (bit 6 faces left, bit 2 airborne, bit 1 invincible), action $80, pose $83, weapon $C9.
  Enemies: 8 slots, occupied = $73 & bit(i); pose $438+i (index into the size tables), x $460+i, y $480+i (feet),
  hp $490+i, type $400+i, flags $498+i.
  Lanterns: 4 slots, occupied = $C0 & bit(i), state $4D1+i (bit 3 = gone, bit 2 = item falling), x $4D9+i,
  y $4E1+i, item id $4C9+i (low nibble), column record $4F1+i.
  Thrown weapons: 3 slots, out = $C8 & bit(i), x $4BB+i, y $4BE+i.
ROM tables (bank 0, at $B300 / $B400 when bank 0 is mapped = file offsets 0x3310 / 0x3410, exactly the Lua arrays):
  half-width XR[pose] and height YR[pose]; thrown weapon size $E605[weapon & $7F] (bank 7).

Formulas (ROM, signed 8-bit like the 6502 code, screen coordinates):
  hurt_ryu ($E144):  |ex - rx| < XR  and  (0 <= ry - ey < $90  or  0 < ey - ry < YR)
                     = enemy box [ex-XR, ex+XR] x [ey-YR, ey] overlaps Ryu's line [ry-$90, ry]  (Lua: same box)
                     skipped while ryu_flags bit 1 (invincible), weapon $84 (Invincible Fire-Wheel) or action 7.
  sword_hit ($DECF), only on poses 7 (stand/jump slash) and $0A (crouch slash):
                     facing right: 0 <= (ex - XR) - rx < 32 ; facing left: 0 <= rx - XR - ex < 32
                     (the enemy's NEAR edge must be inside the 32-px blade; Lua draws the blade [rx, rx+32] x
                     [ry-$90, ry-$90+16]); vertical: dy = ey - ry, 0 <= dy < $92 or 0 < -dy < max($91, $92).
  spin_hit ($DE7B), action 7 (Jump & Slash spin) or weapon $84:
                     -(XR + 8) < ex - rx < XR + 12  and  (0 <= ey - ry < YR  or  0 < ry - ey <= 24)
                     (Lua: Ryu box rx +-9 x [ry-$90, ry] while pose $0C-$0F with weapon $85 - an approximation).
  lantern slash ($DAA2): pose 7 or $27: facing right 0 <= lx - rx < 32 (left: 0 <= rx - lx < 32) and
                     |(ry - 8) - ly| < 16;  spin / $84: |lx - rx| < 16 and |ly - ry| < 17;
                     thrown weapon i: |lx - tx| < S and |ly - ty| < S, S = $E605[weapon&$7F] (Lua: weapon box
                     x +- S, [ty - S, ty]).
  lantern pickup ($DB8A): |rx - lx| < 12 and |ry - ly| < 17.
Platforms / walls: the 16x16 collision map at $300 (192 bytes = 32 columns x 6 rows of nibbles; feos's ViewBG):
  tile_kinds() decodes it: 1 right wall, 2 left wall, 3 both, 4/5/6 corners, 7 floor, 8 ejecting block, 9 ladder,
  12-15 exits.
"""
from __future__ import annotations

from functools import lru_cache

from . import common as C

BIT = (1, 2, 4, 8, 16, 32, 64, 128)


@lru_cache(None)
def _rom():
    return C.ROM.read_bytes()


@lru_cache(None)
def size_tables():
    d = _rom()
    xr = list(d[0x3310:0x3310 + 256])
    yr = list(d[0x3410:0x3410 + 256])
    b7 = 16 + 7 * 0x4000
    wsize = list(d[b7 + 0xE605 - 0xC000:b7 + 0xE605 - 0xC000 + 8])
    return xr, yr, wsize


def _s8(v):
    v &= 0xFF
    return v - 256 if v >= 128 else v


def ryu(ram) -> dict:
    return {"x": ram[0x86], "y": ram[0x8A], "h": ram[0x90], "up": ram[0x91], "down": ram[0x92],
            "left": bool(ram[0x84] & 0x40), "air": bool(ram[0x84] & 0x04), "inv": bool(ram[0x84] & 0x02),
            "action": ram[0x80], "pose": ram[0x83], "weapon": ram[0xC9], "hp": ram[0x65], "ninpo": ram[0x64]}


def enemies(ram) -> list[dict]:
    xr, yr, _ = size_tables()
    out = []
    for i in range(8):
        if not ram[0x73] & BIT[i]:
            continue
        p = ram[0x438 + i]
        out.append({"slot": i, "type": ram[0x400 + i], "pose": p, "x": ram[0x460 + i], "y": ram[0x480 + i],
                    "xr": xr[p], "yr": yr[p], "hp": ram[0x490 + i], "flags": ram[0x498 + i],
                    "box": (ram[0x460 + i] - xr[p], ram[0x480 + i] - yr[p], ram[0x460 + i] + xr[p], ram[0x480 + i])})
    return out


def lanterns(ram) -> list[dict]:
    out = []
    for i in range(4):
        if not ram[0xC0] & BIT[i]:
            continue
        st = ram[0x4D1 + i]
        out.append({"slot": i, "x": ram[0x4D9 + i], "y": ram[0x4E1 + i], "item": ram[0x4C9 + i] & 0x0F,
                    "state": st, "gone": bool(st & 8), "falling": bool(st & 4), "rec": ram[0x4F1 + i],
                    "box": (ram[0x4D9 + i] - 12, ram[0x4E1 + i] - 16, ram[0x4D9 + i] + 12, ram[0x4E1 + i])})
    return out


def thrown(ram) -> list[dict]:
    _, _, ws = size_tables()
    s = ws[ram[0xC9] & 0x07] if (ram[0xC9] & 0x7F) < 8 else 0
    return [{"slot": i, "x": ram[0x4BB + i], "y": ram[0x4BE + i], "size": s}
            for i in range(3) if ram[0xC8] & BIT[i]]


def hurts(ram, en) -> bool:
    """Would enemy `en` (from enemies()) hurt Ryu this frame (ROM hurt_ryu test, ignoring the skip conditions)?"""
    r = ryu(ram)
    dx = abs(_s8(en["x"] - r["x"]))
    if dx >= en["xr"]:
        return False
    d = _s8(r["y"] - en["y"])
    return d < r["h"] if d >= 0 else -d < en["yr"]


def can_be_hurt(ram) -> bool:
    r = ryu(ram)
    return not (r["inv"] or r["weapon"] == 0x84 or r["action"] == 7)


def sword_hits(ram, en) -> bool:
    """ROM sword_hit for the CURRENT pose (True only on the hit poses 7 / $0A)."""
    r = ryu(ram)
    if r["pose"] not in (7, 0x0A):
        return False
    d = (en["x"] - en["xr"] - r["x"]) if not r["left"] else (r["x"] - en["xr"] - en["x"])
    if not (0 <= (d & 0xFF) < 32):
        return False
    dy = _s8(en["y"] - r["y"])
    return dy < r["down"] if dy >= 0 else -dy < max(r["up"], r["down"])


def sword_would_hit(ram, en, facing_left=None, ry=None, rx=None, up=0x18, down=0x18) -> bool:
    """Geometry-only version for planning: a slash from (rx, ry) facing `facing_left` (defaults from RAM)."""
    r = ryu(ram)
    rx = r["x"] if rx is None else rx
    ry = r["y"] if ry is None else ry
    fl = r["left"] if facing_left is None else facing_left
    d = (en["x"] - en["xr"] - rx) if not fl else (rx - en["xr"] - en["x"])
    if not (0 <= d < 32):
        return False
    dy = en["y"] - ry
    return dy < down if dy >= 0 else -dy < max(up, down)


def spin_hits(ram, en) -> bool:
    r = ryu(ram)
    if not (r["action"] == 7 or r["weapon"] == 0x84):
        return False
    dx = _s8(en["x"] - r["x"])
    if not (-(en["xr"] + 8) < dx < en["xr"] + 12):
        return False
    dy = _s8(en["y"] - r["y"])
    return dy < en["yr"] if dy >= 0 else -dy <= 24


def lantern_slash(ram, ln, pose=None, rx=None, ry=None, facing_left=None) -> bool:
    r = ryu(ram)
    pose = r["pose"] if pose is None else pose
    rx = r["x"] if rx is None else rx
    ry = r["y"] if ry is None else ry
    fl = r["left"] if facing_left is None else facing_left
    if pose not in (7, 0x27):
        return False
    d = (ln["x"] - rx) if not fl else (rx - ln["x"])
    return 0 <= d < 32 and abs((ry - 8) - ln["y"]) < 16


def lantern_pickup(ram, ln) -> bool:
    r = ryu(ram)
    return abs(r["x"] - ln["x"]) < 12 and abs(r["y"] - ln["y"]) < 17


def tile_kinds(ram) -> list[list[int]]:
    """The collision map at $300: 32 columns x 12 half-rows (16 px) of kinds (see module doc). Column order is the
    ring buffer's (column c = bytes $300 + 6c .. 6c+5, hi nibble then lo nibble); screen column 0 is ring column
    ($5F / 6) when the room has scrolled - see GetCell in the Lua script ($E7CC table + $5F)."""
    out = []
    for c in range(32):
        col = []
        for line in range(6):
            v = ram[0x300 + c * 6 + line]
            col += [v >> 4, v & 15]
        out.append(col)
    return out


def snapshot(ram) -> dict:
    """Everything above for one frame (for logs / planners)."""
    en = enemies(ram)
    for x in en:
        x["hurts"] = hurts(ram, x)
        x["sword"] = sword_would_hit(ram, x)
    return {"ryu": ryu(ram), "enemies": en, "lanterns": lanterns(ram), "thrown": thrown(ram)}
