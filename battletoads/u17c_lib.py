"""Track C (integration, 2026-10-10) helpers.  Nothing here writes memory; everything is inputs on savestates.
Owner of u17c_*.py, logs/fix/u17c_*, knowledge/u17c_notes.md, segments logs/pbeam_C*.json, bookmarks states/C*.State, routes up17a*."""
import hashlib
import json
import os
import shutil

from toads.emulator import BizHawk, LOGS_DIR, STATES_DIR, PROJECT  # noqa: F401

FIX = LOGS_DIR / "fix"
INTRO = [("Right", 1170), ("Start", 4), ("A", 727), ("", 16)]          # assemble.py's fixed intro (1,917 frames)
F8 = {"level": 0x10, "timer": 0x0B, "x": 0x3FD, "xh": 0x3EE, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "st": 0x4B1,
      "hp": 0x51A, "face": 0x4A2, "lives": 0x11, "camlo": 0x89, "camhi": 0x8A}
for _k in range(6):
    F8[f"sc{_k}"] = 0x5F4 + _k
for _q in range(1, 15):
    F8[f"id{_q}"] = 0x3C1 + _q
    F8[f"ox{_q}"] = 0x3FD + _q
    F8[f"oh{_q}"] = 0x439 + _q


def bt(s):
    return tuple(x for x in s.replace(",", "+").split("+") if x)


def segj(name):
    return json.load(open(LOGS_DIR / f"pbeam_{name}.json"))


def seg(name):
    return [b.replace(",", "+") for b in segj(name)["inputs"]]


def route_inputs(names):
    ins = []
    for b, n in INTRO:
        ins += [b] * n
    for nm in names:
        ins += seg(nm)
    return ins


def banned1(b):
    s = set(bt(b))
    return ("Left" in s and "Right" in s) or ("Up" in s and "Down" in s) or "Start" in s


def banned(inputs):
    lr = ud = st = sel = 0
    for b in inputs:
        t = set(bt(b))
        lr += {"Left", "Right"} <= t
        ud += {"Up", "Down"} <= t
        st += "Start" in t
        sel += "Select" in t
    return lr, ud, st, sel


def write_json(path, d, indent=None):
    """utf-8, temp file + rename, keeps a .backup of what was there"""
    path = str(path)
    if os.path.exists(path):
        shutil.copyfile(path, path + ".backup")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=indent)
    os.replace(tmp, path)


def write_seg(name, d):
    assert name.startswith("C"), "track C only writes pbeam_C*.json"
    write_json(LOGS_DIR / f"pbeam_{name}.json", d)


def toad(m):
    return dict(level=m[0x10], x=m[0x3FD] | m[0x3EE] << 8, h=m[0x439], H=m[0x439] | m[0x42A] << 8, depth=m[0x41B], z=m[0x475], hp=m[0x51A], lives=m[0x11],
                score=int("".join(str(m[0x5F4 + k] & 15) for k in range(6))), t0b=m[0x0B], t0c=m[0x0C], t1a=m[0x1A], rng=bytes(m[0x25:0x29]).hex())


def key(m):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x41B], m[0x475], m[0x51A], m[0x10], m[0x11])


def cut(m):
    return bytes(m[:0x100]) + bytes(m[0x200:])


def diff(a, b, skip_stack=True):
    return [i for i in range(0x800) if a[i] != b[i] and not (skip_stack and 0x100 <= i < 0x200)]


class Log:
    def __init__(self, name):
        self.f = open(FIX / name, "w", encoding="utf-8")

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        self.f.write(s + "\n")
        self.f.flush()


def placed_stage(stage, lv, hp, x, LVL):
    """the next level's placement detector: level byte LVL, then toad hp 0 / x 0, then hp > 0 and x > 0 -> 3"""
    if stage == 0 and lv == LVL:
        stage = 1
    if stage == 1 and hp == 0 and x == 0:
        stage = 2
    if stage == 2 and hp > 0 and x > 0:
        stage = 3
    return stage
