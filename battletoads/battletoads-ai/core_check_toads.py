"""Accuracy check: does a verified input file still play on BizHawk's accurate NES core (NesHawk)?

The routes were built and verified on BizHawk 2.11.1's default NES core, quickerNES. This tool replays the same
power-on input list on any core through the normal bridge, keeps the whole 2 KB of RAM for EVERY frame, and compares
two such captures: the first frame that differs, which bytes, lag frames, level changes, and RAM SHA-1 at every level
change and every 600 frames.

    python core_check_toads.py run  <tag> [--core quickerNES|NesHawk] [--lead N] [--inputs logs/up14.inputs.txt]
                                           [--tail 800] [--stop F]
        replay from power-on; N blank frames first (negative N drops the first -N frames); after the list ends,
        mash A every other frame for --tail frames (skips the Queen's speech, reaches the cut to T. Bird).
        writes logs/fix/core_<tag>.ram (frame f at byte offset f*2048; frame 0 = before the first step),
               logs/fix/core_<tag>.meta.tsv (frame, emu.framecount, emu.lagcount, islagged) and core_<tag>.json
    python core_check_toads.py cmp  <tagA> <tagB> [--shift K]
        compare capture B against A: B's frame f+K against A's frame f. Writes logs/fix/core_cmp_<A>_<B>[_sK].json
    python core_check_toads.py movie <tag> <movie.bk2> [--core NesHawk] [--frames N] [--keep-header]
        hands-off check: play a .bk2 with no joypad calls at all (a generated Lua logs the core, the level byte and
        a RAM hash every 600 frames). By default the movie is copied with its "Core" header rewritten to --core,
        because BizHawk loads the core NAMED IN THE MOVIE, whatever the config prefers (--keep-header shows that).
    python core_check_toads.py info <tag>
        print a capture's summary (core, level changes, lag totals).
    python core_check_toads.py elastic <tag> [--ref q] [--core NesHawk]
        lag-compensated replay: the reference capture's inputs by POLLED frame (the k-th frame on which the game reads
        the controller gets what the reference's k-th polled frame got; a lag frame gets the same input again). Shows
        where the GAME first differs once the cores' different load times are out of the way.
    python core_check_toads.py port <tag> [--ref q] [--core NesHawk] [--mods-from <earlier port>] [--end-steer 900]
        the lag-compensated replay plus Select re-rolls wherever the dice make the toad's or a tracked enemy's track
        leave the reference's (rngfit.py's method; savestates for the search only). --end-steer S: on the Queen's last
        hit, hand the live emulator to track END's end_tail.append_tail for S seconds (the ending's dice differ per
        core). Writes logs/fix/core_<tag>.inputs.txt (a plain power-on input list for that core) and core_<tag>.json.
        VERIFY it afterwards: `run` it twice on that core with --tail 0 - the two SHA-1s at the end must be equal.
    python core_check_toads.py pcmp <tagA> <tagB>
        compare two captures by polled frame (fair across cores): table at every level change and every 600 frames
        with both SHA-1s -> logs/fix/core_pcmp_<A>_<B>.md / .json
    python core_check_toads.py bk2 <tag> [--core C] [--lead 1]
        a capture's input list as a .bk2 whose header names the core -> logs/fix/core_<tag>_<core>.bk2

`run`, `cmp`, `pcmp`, `movie` and `elastic` never load a savestate or write memory. `port` loads savestates while it
searches; its output is only trusted after the two `run` replays. Results: knowledge/core_check_toads.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
import zipfile
from pathlib import Path

import numpy as np

import toads.emulator as emu_mod
from toads.emulator import PROJECT, LOGS_DIR, BIZHAWK_DIR, EMUHAWK, ROM

FIX = LOGS_DIR / "fix"
RAM = 0x800
LEVEL = 0x10                      # level byte
RNG = (0x25, 0x26, 0x27, 0x28)    # the idle-loop dice
KEY = [0x10, 0x11, 0x87, 0x88, 0x89, 0x8A, 0x3B5, 0x3FD, 0x3EE, 0x41B, 0x439, 0x493, 0x51A]   # level, lives, camera, toad
NAMES = {0x0B: "timer lo", 0x0C: "timer hi", 0x10: "level", 0x11: "lives", 0x23: "routine lo", 0x24: "routine hi",
         0x25: "rng0", 0x26: "rng1", 0x27: "rng2", 0x28: "rng3", 0x29: "pad", 0x87: "cam x lo", 0x88: "cam x hi",
         0x89: "cam y lo", 0x8A: "cam y hi", 0x3B5: "toad anim", 0x3FD: "toad x", 0x3EE: "toad x hi",
         0x41B: "toad y", 0x439: "toad height", 0x493: "toad depth", 0x51A: "toad hp", 0x565: "toad speed",
         0x586: "queen counter", 0x585: "checkpoint"}

EXTRA_LUA = r'''
  elseif cmd == "coreinfo" then
    local names = {}
    local d = memory.getmemorydomainlist()
    for i = 0, 64 do if d[i] ~= nil then names[#names+1] = tostring(d[i]) end end
    local board = "?"
    pcall(function() board = tostring(emu.getboardname()) end)
    local regs = {}
    pcall(function() for k, _ in pairs(emu.getregisters()) do regs[#regs+1] = tostring(k) end end)
    table.sort(regs)
    local pref = "?"
    pcall(function() pref = tostring(client.getconfig().PreferredCores["NES"]) end)
    send("sys=" .. tostring(emu.getsystemid()) .. ";board=" .. board .. ";pref=" .. pref ..
         ";framecount=" .. emu.framecount() .. ";domains=" .. table.concat(names, "|") ..
         ";regs=" .. table.concat(regs, "|"))
  elseif cmd == "capstep" then
    -- one frame with the given buttons; reply "<framecount> <lagcount> <islagged> <2 KB of RAM as hex>"
    local t = parse_buttons(rest ~= "" and rest or "-")
    joypad.set(t, 1)
    emu.frameadvance()
    local arr = memory.read_bytes_as_array(0, 2048, "RAM")
    send(emu.framecount() .. " " .. emu.lagcount() .. " " .. (emu.islagged() and 1 or 0) .. " " .. tohex(arr))
  elseif cmd == "capnow" then
    local arr = memory.read_bytes_as_array(0, 2048, "RAM")
    send(emu.framecount() .. " " .. emu.lagcount() .. " " .. (emu.islagged() and 1 or 0) .. " " .. tohex(arr))
'''

MOVIE_LUA = r'''-- generated by core_check_toads.py: hands-off movie watcher (never touches the joypad)
local target = tonumber(userdata.get("frames") or "0")
local out = userdata.get("out")
local f = io.open(out, "w")
local names = {}
local d = memory.getmemorydomainlist()
for i = 0, 64 do if d[i] ~= nil then names[#names+1] = tostring(d[i]) end end
local board = "?"
pcall(function() board = tostring(emu.getboardname()) end)
local pref = "?"
pcall(function() pref = tostring(client.getconfig().PreferredCores["NES"]) end)
local mode = "?"
pcall(function() mode = tostring(movie.mode()) end)
local mlen = "?"
pcall(function() mlen = tostring(movie.length()) end)
f:write("info\tsys=" .. tostring(emu.getsystemid()) .. ";board=" .. board .. ";pref=" .. pref .. ";movie=" .. mode ..
        ";movielen=" .. mlen .. ";framecount=" .. emu.framecount() .. ";domains=" .. table.concat(names, "|") .. "\n")
client.speedmode(6400)
client.unpause()
local prev = -1
while emu.framecount() < target do
  emu.frameadvance()
  local fc = emu.framecount()
  local lv = memory.read_u8(16, "RAM")
  if lv ~= prev or fc % 600 == 0 or fc == target then
    f:write(fc .. "\t" .. lv .. "\t" .. emu.lagcount() .. "\t" .. memory.hash_region(0, 2048, "RAM") .. "\n")
    f:flush()
    prev = lv
  end
end
f:close()
client.exit()
'''


def read_inputs(path: Path) -> list[tuple[str, ...]]:
    rows = []
    for l in Path(path).read_text().splitlines():
        if l.startswith("#"):
            continue
        rows.append(tuple(x for x in l.replace("+", ",").split(",") if x))
    return rows


def banned(rows) -> int:
    n = 0
    for r in rows:
        s = set(r)
        if {"Left", "Right"} <= s or {"Up", "Down"} <= s:
            n += 1
    return n


def derived_bridge() -> Path:
    """bridge.lua + three read-only commands (coreinfo, capstep, capnow), written to logs/fix/. bridge.lua itself is
    not touched."""
    FIX.mkdir(parents=True, exist_ok=True)
    src = (PROJECT / "bridge.lua").read_text(encoding="utf-8")
    anchor = '  elseif cmd == "quit" then'
    assert anchor in src, "bridge.lua changed: quit handler not found"
    out = FIX / "bridge_corecheck.lua"
    tmp = out.with_suffix(".lua.tmp")
    tmp.write_text(src.replace(anchor, EXTRA_LUA.rstrip("\n") + "\n" + anchor, 1), encoding="utf-8")
    tmp.replace(out)
    return out


def parse_info(s: str) -> dict:
    d = {}
    for part in s.split(";"):
        k, _, v = part.partition("=")
        d[k] = v
    d["domains"] = d.get("domains", "").split("|")
    d["regs"] = [r for r in d.get("regs", "").split("|") if r]
    # NesHawk exposes the PPU's address space as a memory domain; quickerNES does not
    d["core_seen"] = "NesHawk" if "PPU Bus" in d["domains"] else "quickerNES"
    return d


def sha(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


# ------------------------------------------------------------------ run
def run(a):
    FIX.mkdir(parents=True, exist_ok=True)
    rows = read_inputs(PROJECT / a.inputs)
    nb = banned(rows)
    lead = a.lead
    seq = ([()] * lead + rows) if lead >= 0 else rows[-lead:]
    n_inputs = len(seq)
    tail = [("A",), ()] * (a.tail // 2)
    seq = seq + tail
    if a.stop:
        seq = seq[:a.stop]
    if a.core:
        os.environ["TOADS_CORE"] = a.core
    else:
        os.environ.pop("TOADS_CORE", None)
    emu_mod.BRIDGE_LUA = derived_bridge()
    e = emu_mod.BizHawk(log_name=f"fix_core_{a.tag}.log", fields={})
    info = parse_info(e.cmd("coreinfo"))
    print(f"[{a.tag}] core wanted {a.core or '(config default)'}; loaded: {info['core_seen']} "
          f"(board {info['board']}, pref {info['pref']}, framecount at connect {info['framecount']})", flush=True)
    if a.core and info["core_seen"].lower() != a.core.lower():
        e.close()
        raise SystemExit(f"wrong core loaded: wanted {a.core}, memory domains say {info['core_seen']}")
    ram_path = FIX / f"core_{a.tag}.ram"
    meta_path = FIX / f"core_{a.tag}.meta.tsv"
    t0 = time.time()
    level_changes = []
    every600 = {}
    with open(ram_path, "wb") as fr, open(meta_path, "w") as fm:
        fc, lag, isl, hx = e.cmd("capnow").split(" ")
        ram = bytes.fromhex(hx)
        fr.write(ram)
        fm.write(f"0\t{fc}\t{lag}\t{isl}\n")
        prev_lv = ram[LEVEL]
        fc0 = int(fc)
        for i, b in enumerate(seq):
            fc, lag, isl, hx = e.cmd("capstep " + (",".join(b) or "-")).split(" ")
            ram = bytes.fromhex(hx)
            assert len(ram) == RAM
            fr.write(ram)
            f = i + 1
            fm.write(f"{f}\t{fc}\t{lag}\t{isl}\n")
            lv = ram[LEVEL]
            if lv != prev_lv:
                level_changes.append({"frame": f, "from": prev_lv, "to": lv, "sha1": sha(ram), "lag": int(lag)})
                print(f"[{a.tag}] frame {f}: level byte {prev_lv} -> {lv}  lag {lag}  sha1 {sha(ram)[:8]}", flush=True)
                prev_lv = lv
            if f % 600 == 0:
                every600[f] = sha(ram)
            if f == n_inputs:
                end_sha = sha(ram)
                end_lag = int(lag)
                print(f"[{a.tag}] end of the input list (frame {f}): sha1 {end_sha}  level {lv}  lag {lag}", flush=True)
            if f % 5000 == 0:
                print(f"[{a.tag}] frame {f}  level {lv}  lag {lag}  {f / (time.time() - t0):.0f} fps", flush=True)
    e.close()
    summ = {"tag": a.tag, "inputs": a.inputs, "input_frames": len(rows), "banned_presses": nb, "lead": lead,
            "tail_mash_A": a.tail, "frames_captured": len(seq), "core_wanted": a.core, "core_info": info,
            "framecount_at_connect": fc0, "level_changes": level_changes, "sha1_every_600": every600,
            "sha1_at_input_end": locals().get("end_sha"), "lag_at_input_end": locals().get("end_lag"),
            "seconds": round(time.time() - t0, 1)}
    (FIX / f"core_{a.tag}.json").write_text(json.dumps(summ, indent=1))
    print(f"[{a.tag}] done: {len(seq)} frames in {time.time() - t0:.0f}s -> {ram_path}", flush=True)


# ------------------------------------------------------------------ lag-compensated replay
def soft_mask():
    """Bytes that depend on WHERE in the idle loop the frame snapshot is taken (the dice, an idle counter, the stack):
    they differ between cores on frames whose game state is otherwise identical."""
    m = np.ones(RAM, dtype=bool)
    m[list(RNG)] = False
    m[0x75] = False
    m[0x100:0x200] = False
    return m


def elastic(a):
    """Feed the reference run's inputs to another core by POLLED frame: the k-th frame on which the game reads the
    controller gets the input the reference's k-th polled frame got. Lag frames (loads, slowdown) may then differ in
    number between the cores without shifting the inputs against the game. Reports where the game state first
    differs (dice aside) and how many frames each core needs for the same stretch of game."""
    FIX.mkdir(parents=True, exist_ok=True)
    refram, refmeta, refsum = load(a.ref)
    rows = read_inputs(PROJECT / refsum["inputs"])
    lead = refsum["lead"]
    seq = ([()] * lead + rows) if lead >= 0 else rows[-lead:]
    seq = seq + [("A",), ()] * (refsum["tail_mash_A"] // 2)
    seq = seq[:len(refram) - 1]
    reflag = refmeta[:, 3]
    # reference frames whose input was read. quickerNES reports one controller read on the very first frame after
    # power-on (frame 1) that NesHawk does not have; it is not a poll by the game (nothing is running yet): skip it.
    polled = [f for f in range(a.first_poll, len(seq) + 1) if reflag[f] == 0]
    print(f"[{a.tag}] reference {a.ref}: {len(seq)} frames, {len(polled)} polled, {len(seq) - len(polled)} lag", flush=True)
    os.environ["TOADS_CORE"] = a.core
    emu_mod.BRIDGE_LUA = derived_bridge()
    e = emu_mod.BizHawk(log_name=f"fix_core_{a.tag}.log", fields={})
    info = parse_info(e.cmd("coreinfo"))
    print(f"[{a.tag}] loaded: {info['core_seen']} (board {info['board']})", flush=True)
    if info["core_seen"].lower() != a.core.lower():
        e.close()
        raise SystemExit("wrong core loaded")
    mask = soft_mask()
    ram_path = FIX / f"core_{a.tag}.ram"
    meta_path = FIX / f"core_{a.tag}.meta.tsv"
    sent = []
    pairs = []                  # (this core's frame, reference frame) for every polled frame
    k = 0                       # next polled reference frame to feed
    t = 0
    t0 = time.time()
    level_changes, marks = [], []
    first_soft = first_hard = first_other = None
    n_other = 0
    hard_run = 0                # consecutive polled frames whose state differs
    diverged_at = None
    ref_levels = {c["frame"]: c for c in refsum["level_changes"]}
    lagn = 0
    with open(ram_path, "wb") as fr, open(meta_path, "w") as fm:
        fc, lag, isl, hx = e.cmd("capnow").split(" ")
        ram = bytes.fromhex(hx)
        fr.write(ram)
        fm.write(f"0\t{fc}\t{lag}\t{isl}\t0\n")
        prev_lv = ram[LEVEL]
        while k < len(polled) and t < a.max_frames:
            rf = polled[k]
            b = seq[rf - 1]
            fc, lag, isl, hx = e.cmd("capstep " + (",".join(b) or "-")).split(" ")
            ram = bytes.fromhex(hx)
            fr.write(ram)
            t += 1
            sent.append(b)
            isl = int(isl)
            lagn += isl
            fm.write(f"{t}\t{fc}\t{lag}\t{isl}\t{rf if not isl else 0}\n")
            lv = ram[LEVEL]
            if lv != prev_lv:
                level_changes.append({"frame": t, "from": prev_lv, "to": lv, "ref_polled_frame": rf, "lag": lagn})
                prev_lv = lv
            if isl:
                continue                                    # input not read: offer the same one again
            pairs.append((t, rf))
            # this core's polled frame k against the reference's polled frame k
            cur = np.frombuffer(ram, dtype=np.uint8)
            ref = refram[rf]
            neq = cur != ref
            anyhard = bool(neq[mask].any())
            # "hard" = the bytes a run lives by: level, lives, camera, the toad's position/animation/health
            hard = bool(neq[KEY].any()) if a.key_only else anyhard
            soft = bool(neq[~mask].any())
            if anyhard:
                n_other += 1
                if first_other is None:
                    lst, cnt = diff_bytes(ref, cur)
                    first_other = {"frame": t, "ref_frame": rf, "bytes_differing": cnt, "bytes": lst}
            if soft and first_soft is None:
                first_soft = {"frame": t, "ref_frame": rf}
            if hard:
                hard_run += 1
                if first_hard is None:
                    lst, cnt = diff_bytes(ref, cur)
                    first_hard = {"frame": t, "ref_frame": rf, "polled_index": k, "bytes_differing": cnt, "bytes": lst,
                                  "note": "a = reference, b = this core"}
                    print(f"[{a.tag}] first state difference (dice aside): frame {t} (reference frame {rf}), "
                          f"{cnt} bytes: " + ", ".join(f"{x['addr']} {x['name']} {x['a']}->{x['b']}" for x in lst[:10]), flush=True)
                if hard_run == a.patience and diverged_at is None:
                    lst, cnt = diff_bytes(ref, cur)
                    pt, pr = pairs[-a.patience]
                    diverged_at = {"frame": pt, "ref_frame": pr, "polled_index": k - a.patience + 1, "bytes_then": cnt,
                                   "last_same": {"frame": pairs[-a.patience - 1][0], "ref_frame": pairs[-a.patience - 1][1]}
                                   if len(pairs) > a.patience else None}
                    print(f"[{a.tag}] DIVERGED for good: {a.patience} polled frames in a row differ, starting at frame "
                          f"{diverged_at['frame']} (reference frame {diverged_at['ref_frame']})", flush=True)
            else:
                if hard_run and diverged_at is None:
                    marks.append({"frame": t, "ref_frame": rf, "resynced_after": hard_run})
                hard_run = 0
            if rf in ref_levels or k % 3000 == 0:
                print(f"[{a.tag}] frame {t} = reference frame {rf} (offset {t - rf:+d}), level {lv} (ref {int(ref[LEVEL])}), "
                      f"lag {lagn} (ref {int(reflag[:rf + 1].sum())}), toad/camera {'DIFFER' if hard else 'same'}, "
                      f"{int(neq[mask].sum())} bytes differ"
                      f"{' [level change in the reference]' if rf in ref_levels else ''}  {t / (time.time() - t0):.0f} fps", flush=True)
            k += 1
            if diverged_at is not None and t - diverged_at["frame"] > a.after:
                print(f"[{a.tag}] stopping {a.after} frames after the divergence", flush=True)
                break
    end_sha = sha(ram)
    e.close()
    ip = FIX / f"core_{a.tag}.inputs.txt"
    tmp = ip.with_suffix(".txt.tmp")
    tmp.write_text(f"# frames={len(sent)} lag-compensated from {a.ref} for {a.core}\n" + "\n".join(",".join(b) for b in sent) + "\n")
    tmp.replace(ip)
    summ = {"tag": a.tag, "mode": "elastic", "ref": a.ref, "inputs": f"logs/fix/core_{a.tag}.inputs.txt", "input_frames": len(sent),
            "banned_presses": banned(sent), "lead": 0, "tail_mash_A": 0, "frames_captured": t, "core_wanted": a.core,
            "core_info": info, "level_changes": level_changes, "first_soft_difference": first_soft,
            "first_state_difference": first_hard, "first_any_difference": first_other,
            "polled_frames_with_any_difference": n_other, "diverged": diverged_at, "transient_differences": marks[:200],
            "polled_fed": k, "polled_total": len(polled), "lag_frames": lagn, "sha1_at_end": end_sha,
            "seconds": round(time.time() - t0, 1)}
    (FIX / f"core_{a.tag}.json").write_text(json.dumps(summ, indent=1))
    print(f"[{a.tag}] fed {k}/{len(polled)} polled inputs in {t} frames ({lagn} lag). diverged: {diverged_at}", flush=True)


# ------------------------------------------------------------------ port: lag compensation + Select re-rolls
TRACK_IDS = {0x7D, 0x7E, 0x7B, 0x5C, 0x62}     # Robo-Manus, Dark Queen, Buzzball, Hornhead, walker (rngfit's list + queen)


def gkey(m, loose=False):
    """rngfit.py's key: the toad's x, height, y, z, health, the level; tracked enemies' (id, x, height, health) in any
    slot order; in Level 13 the Queen's hit counter. loose: the enemies' id and health only (not where they are)."""
    if not isinstance(m, (bytes, bytearray)):
        m = bytes(m)                       # a numpy row: uint8 << 8 would overflow
    k = (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x41B], m[0x475], m[0x51A], m[0x10], m[0x586] if m[0x10] == 13 else 0)
    if loose:
        objs = tuple(sorted((m[0x3C1 + q], m[0x51A + q]) for q in range(2, 15) if m[0x3C1 + q] in TRACK_IDS))
    else:
        objs = tuple(sorted((m[0x3C1 + q], m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q])
                            for q in range(2, 15) if m[0x3C1 + q] in TRACK_IDS))
    return k + objs


class Porter:
    """Plays the reference's polled inputs on another core, and where the game's dice make the two part, goes back
    and toggles Select on an earlier frame (Select does nothing in play; it changes that frame's CPU time, and with
    it every later roll) until the reference's track holds again. Savestates are used for the search only: the
    resulting input list is afterwards replayed from power-on with `run`."""

    def __init__(self, a):
        self.a = a
        self.refram, refmeta, self.refsum = load(a.ref)
        rows = read_inputs(PROJECT / self.refsum["inputs"])
        lead = self.refsum["lead"]
        seq = ([()] * lead + rows) if lead >= 0 else rows[-lead:]
        seq = seq + [("A",), ()] * (self.refsum["tail_mash_A"] // 2)
        self.seq = seq[:len(self.refram) - 1]
        reflag = refmeta[:, 3]
        self.polled = [f for f in range(a.first_poll, len(self.seq) + 1) if reflag[f] == 0]
        self.K = len(self.polled)
        self.rk_cache = {}
        self.mods = set()          # polled indices whose Select is toggled
        self.tolerated = set()     # polled indices whose mismatch was passing (the tracks met again by themselves)
        self.sent = []
        self.k = self.t = self.lagn = 0
        self.ring = []
        self.ram = b""
        self.level_log = []
        self.repairs = []
        self.trials = 0
        self.lag_run = 0
        self.loose = False         # set when the strict key cannot be restored; cleared at the next level
        self.loose_from = []
        self.loose_spans = []      # (first polled index, last polled index) played with the loose key
        # the reference's own last-hit frame (Queen 0x7E -> dead boss 0x46 in Level 13), as a polled index
        self.kh = None
        R = self.refram
        for f in range(1, len(self.seq) + 1):
            if R[f][LEVEL] == 13:
                ids, pids = bytes(R[f][0x3C1:0x3D0]), bytes(R[f - 1][0x3C1:0x3D0])
                if any(pids[q] == 0x7E and ids[q] == 0x46 for q in range(2, 15)):
                    import bisect
                    self.kh = bisect.bisect_left(self.polled, f)
                    break
        if a.mods_from:
            prev = json.loads((FIX / f"core_{a.mods_from}.json").read_text())
            idx = {f: i for i, f in enumerate(self.polled)}
            self.mods = {idx[f] for f in prev["select_toggles_ref_frames"]}
            self.loose_spans = [tuple(x) for x in prev.get("loose_spans", [])]
            print(f"[{a.tag}] starting with {len(self.mods)} Select toggles from {a.mods_from}", flush=True)

    def is_loose(self, k):
        if self.loose or any(lo <= k <= hi for lo, hi in self.loose_spans):
            return True
        return bool(self.a.loose_level) and int(self.refram[self.polled[min(k, self.K - 1)]][LEVEL]) in self.a.loose_level

    def rk(self, k):
        lz = self.is_loose(k)
        v = self.rk_cache.get((k, lz))
        if v is None:
            v = self.rk_cache[(k, lz)] = gkey(self.refram[self.polled[k]], lz)
        return v

    def inp(self, k):
        b = self.seq[self.polled[k] - 1]
        if k in self.mods:
            b = tuple(x for x in b if x != "Select") if "Select" in b else b + ("Select",)
        return b

    def step(self):
        """one frame. None = lag frame (input not read), else whether the key matches the reference's polled frame"""
        b = self.inp(self.k)
        fc, lag, isl, hx = self.e.cmd("capstep " + (",".join(b) or "-")).split(" ")
        self.prev_ram = self.ram
        self.ram = bytes.fromhex(hx)
        del self.sent[self.t:]
        self.sent.append(b)
        self.t += 1
        if isl == "1":
            self.lagn += 1
            self.lag_run += 1
            if self.lag_run > 3000:
                raise RuntimeError(f"3000 lag frames in a row at frame {self.t}: the game is not reading the controller")
            return None
        self.lag_run = 0
        ok = gkey(self.ram, self.is_loose(self.k)) == self.rk(self.k)
        self.k += 1
        return ok

    def save(self):
        sid = self.e.cmd("msave")
        self.ring.append({"k": self.k, "t": self.t, "lagn": self.lagn, "sid": sid})
        while len(self.ring) > self.a.ring:
            old = self.ring.pop(0)
            self.e.cmd(f"mfree {old['sid']}")

    def restore(self, ent, drop_later):
        self.e.cmd(f"mload {ent['sid']}")
        self.prev_ram = None
        self.k, self.t, self.lagn = ent["k"], ent["t"], ent["lagn"]
        self.lag_run = 0
        if drop_later:
            keep = []
            for x in self.ring:
                if x["k"] <= ent["k"]:
                    keep.append(x)
                else:
                    self.e.cmd(f"mfree {x['sid']}")
            self.ring = keep

    def entry_before(self, k):
        best = None
        for x in self.ring:
            if x["k"] <= k:
                best = x
        return best

    def trial(self, js, d):
        """toggle Select on polled frames js and play on: returns how far the reference's track then holds (the polled
        index of the first difference; d + hold + extra + 1 if none that far). The toggles are undone again."""
        ent = self.entry_before(min(js))
        if ent is None:
            return -1
        self.trials += 1
        if self.dirty is None or ent["k"] < self.dirty["k"]:
            self.dirty = ent                                       # self.sent is trial junk from this state on
        self.restore(ent, drop_later=False)
        for j in js:
            self.mods ^= {j}
        goal = min(d + self.a.hold + (self.a.extra if self.want_more else 0), self.K - 1)
        reach = goal + 1
        while self.k <= goal:
            ok = self.step()
            if ok is False and (self.k - 1) not in self.tolerated:
                reach = self.k - 1
                break
        for j in js:
            self.mods ^= {j}
        return reach

    def repair(self, d):
        import random
        rnd = random.Random(d)
        lo = max(self.ring[0]["k"], d - self.a.window, 0) if self.ring else d
        t0 = time.time()
        n0 = self.trials
        need = min(d + self.a.hold, self.K - 1)
        cands = []                                                 # (how far it holds, toggles)
        self.want_more = self.a.best_of > 1
        for j in range(d - 1, lo - 1, -1):                         # one Select, nearest first
            r = self.trial([j], d)
            if r > need:
                cands.append((r, [j]))
                if len(cands) >= self.a.best_of or time.time() - t0 > 120:
                    break
        if not cands:
            span = list(range(lo, d))
            # with the enemy's exact position in the key a multi-press pattern rarely exists (run p3/p5: 1,200 tries,
            # none) and the loose key takes over anyway: do not spend long on it
            n_random = self.a.random_tries if self.is_loose(d) else min(self.a.random_tries, self.a.strict_random)
            for _ in range(n_random):                              # then two to four
                if len(span) < 2:
                    break
                js = sorted(rnd.sample(span, min(len(span), rnd.choice((2, 2, 3, 4)))))
                r = self.trial(js, d)
                if r > need:
                    cands.append((r, js))
                    break
        if not cands:
            self.clean()
            return False
        reach, found = max(cands, key=lambda c: c[0])
        for j in found:
            self.mods ^= {j}
        self.repairs.append({"polled_index": d, "ref_frame": self.polled[d],
                             "select_on_ref_frames": [self.polled[j] for j in found], "loose_key": self.is_loose(d),
                             "holds_polled_frames": reach - d, "candidates": len(cands),
                             "back": d - min(found), "tries": self.trials - n0, "seconds": round(time.time() - t0, 1)})
        more = f" (+{len(found) - 1} more)" if len(found) > 1 else ""
        lk = ", loose key" if self.is_loose(d) else ""
        print(f"[{self.a.tag}] re-roll #{len(self.repairs)} at reference frame {self.polled[d]} "
              f"(level {int(self.refram[self.polled[d]][LEVEL])}{lk}): Select toggled "
              f"{d - min(found)} polled frames earlier{more}, holds {reach - d}+ frames, "
              f"{self.trials - n0} tries, {time.time() - t0:.0f}s", flush=True)
        # throw away everything made while testing and replay cleanly from before the earliest thing any trial touched
        self.clean()
        return True

    def clean(self):
        """back to the earliest savestate a trial started from: everything after it (inputs sent, later savestates)
        was made while testing and is played again with the accepted toggles only"""
        if self.dirty is not None:
            self.restore(self.dirty, drop_later=True)
            self.dirty = None

    def last_hit_now(self):
        """this frame is the Queen's last hit: Level 13, her object 0x7E has just turned into the dead boss 0x46.
        Told from the previous frame's RAM, or (right after a savestate load, when there is none) from the
        reference: its last-hit polled frame, matched here, with the dead boss in this core's object table."""
        m, pm = self.ram, self.prev_ram
        if m[LEVEL] != 13:
            return False
        ids = m[0x3C1:0x3D0]
        if pm:
            pids = pm[0x3C1:0x3D0]
            return any(pids[q] == 0x7E and ids[q] == 0x46 for q in range(2, 15))
        return self.kh is not None and self.k - 1 == self.kh and 0x46 in ids[2:15] and 0x7E not in ids[2:15]

    def steered_ending(self):
        """Track END's ending tool (end_tail.py, knowledge/end_timing.md) on this live emulator: the game is on the
        last-hit frame; it measures the ending here, re-rolls its dice with single presses and returns the inputs from
        the next frame to the cut to Professor T. Bird. The dice differ per core, so the ending is searched per core."""
        import end_tail
        a = self.a
        hit_t = self.t
        print(f"[{a.tag}] frame {hit_t}: the Queen's last hit (reference frame {self.polled[self.k - 1]}); "
              f"steering the ending on this core for up to {a.end_steer}s", flush=True)
        res = end_tail.append_tail(self.e, steer_s=a.end_steer, log=lambda *x: print(f"[{a.tag}]   end:", *x, flush=True))
        tail = [tuple(b for b in row.replace(",", "+").split("+") if b) for row in res["tail"]]
        del self.sent[hit_t:]
        self.sent.extend(tail)
        self.t = hit_t + len(tail)
        # end_tail left the emulator on the T. Bird cut frame; 30 idle frames after it, as assemble's routes have
        for _ in range(30):
            fc, lag, isl, hx = self.e.cmd("capstep -").split(" ")
            self.ram = bytes.fromhex(hx)
            self.sent.append(())
            self.t += 1
        self.ending = {"last_hit": hit_t, "queen_speech_cut": hit_t + res["queen_speech_cut"], "back_on_tower": hit_t + res["back"],
                       "tbird_cut": hit_t + res["tbird_cut"], "tail_frames": res["tbird_cut"], "final_wait": res["wait"],
                       "speech_skip": res["skip"], "reload": res["lag"], "presses": [[hit_t + o, b] for o, b in res["presses"]]}
        print(f"[{a.tag}] ending: last hit {hit_t}, Queen's speech cut {self.ending['queen_speech_cut']}, back on the tower "
              f"{self.ending['back_on_tower']}, cut to T. Bird {self.ending['tbird_cut']} (tail {res['tbird_cut']} frames, "
              f"final wait {res['wait']})", flush=True)

    def write(self, done):
        a = self.a
        ip = FIX / f"core_{a.tag}.inputs.txt"
        tmp = ip.with_suffix(".txt.tmp")
        tmp.write_text(f"# frames={len(self.sent)} ported from {a.ref} to {a.core}: lag-compensated, "
                       f"{len(self.mods)} Select toggles\n" + "\n".join(",".join(b) for b in self.sent) + "\n")
        tmp.replace(ip)
        summ = {"tag": a.tag, "mode": "port", "ref": a.ref, "inputs": f"logs/fix/core_{a.tag}.inputs.txt",
                "input_frames": len(self.sent), "banned_presses": banned(self.sent), "lead": 0, "tail_mash_A": 0,
                "core_wanted": a.core, "core_info": self.info, "complete": done, "polled_fed": self.k,
                "polled_total": self.K, "frames": self.t, "lag_frames": self.lagn,
                "select_toggles_ref_frames": sorted(self.polled[j] for j in self.mods),
                "repairs": self.repairs, "trials": self.trials, "tolerated_mismatch_frames": len(self.tolerated),
                "loose_spans": [list(x) for x in self.loose_spans] + ([[self.loose_from[-1], self.K]] if self.loose else []),
                "ending": self.ending,
                "level_changes": self.level_log, "sha1_at_end": sha(self.ram), "seconds": round(time.time() - self.t0, 1)}
        tmpj = FIX / f"core_{a.tag}.json.tmp"
        tmpj.write_text(json.dumps(summ, indent=1))
        tmpj.replace(FIX / f"core_{a.tag}.json")

    def go(self):
        a = self.a
        os.environ["TOADS_CORE"] = a.core
        emu_mod.BRIDGE_LUA = derived_bridge()
        self.e = e = emu_mod.BizHawk(log_name=f"fix_core_{a.tag}.log", fields={})
        self.info = parse_info(e.cmd("coreinfo"))
        print(f"[{a.tag}] loaded: {self.info['core_seen']} (board {self.info['board']}); {self.K} polled inputs to place", flush=True)
        if self.info["core_seen"].lower() != a.core.lower():
            e.close()
            raise SystemExit("wrong core loaded")
        self.t0 = time.time()
        self.dirty = None
        self.ending = None
        self.prev_ram = None
        self.want_more = False
        self.loose_level = None
        prev_lv = None
        last_report = 0
        stuck = None
        ended = False
        try:
            while self.k < self.K and self.t < a.max_frames:
                ok = self.step()
                lv = self.ram[LEVEL]
                if lv != prev_lv:
                    if prev_lv is not None:
                        rf = self.polled[min(self.k, self.K - 1)]
                        fresh = not any(c["frame"] == self.t and c["to"] == lv for c in self.level_log)
                        self.level_log = [c for c in self.level_log if c["frame"] < self.t]
                        self.level_log.append({"frame": self.t, "from": prev_lv, "to": lv, "next_ref_polled_frame": rf, "lag": self.lagn})
                        if fresh:
                            print(f"[{a.tag}] frame {self.t}: level byte {prev_lv} -> {lv}  (next reference polled frame {rf}, "
                                  f"offset {self.t - rf:+d})  re-rolls so far {len(self.repairs)}", flush=True)
                    if self.loose and prev_lv is not None and lv not in (254, 255) and lv != self.loose_level:
                        self.loose_spans.append((self.loose_from[-1], self.k - 1))
                        self.loose = False
                    prev_lv = lv
                if ok is None:
                    continue
                if ok:
                    if a.end_steer and self.last_hit_now():
                        self.steered_ending()
                        ended = True
                        break
                    if self.k % a.every == 0:
                        self.save()
                    if self.k - last_report >= 3000:
                        last_report = self.k
                        print(f"[{a.tag}] frame {self.t} = reference frame {self.polled[self.k - 1]}, level {lv}, "
                              f"{len(self.repairs)} re-rolls, {self.trials} tries, {time.time() - self.t0:.0f}s", flush=True)
                    continue
                d = self.k - 1
                if d in self.tolerated:
                    continue
                # do the tracks meet again by themselves?
                base = self.entry_before(d)
                kd_ref, kd_cur = self.rk(d), gkey(self.ram)
                if a.verbose:
                    print(f"[{a.tag}] frame {self.t}, reference frame {self.polled[d]}: key differs: reference {kd_ref}  here {kd_cur}", flush=True)
                run_ok, bad = 0, [d]
                while self.k < min(self.K, d + a.look) and run_ok < a.rejoin:
                    o = self.step()
                    if o is None:
                        continue
                    if o:
                        run_ok += 1
                    else:
                        run_ok = 0
                        bad.append(self.k - 1)
                if run_ok >= a.rejoin or self.k >= self.K:
                    self.tolerated.update(bad)
                    print(f"[{a.tag}] reference frame {self.polled[d]}: the tracks part for {bad[-1] - d + 1} polled frames "
                          f"({len(bad)} differ) and meet again by themselves", flush=True)
                    prev_lv = self.ram[LEVEL]
                    continue
                print(f"[{a.tag}] frame {self.t}: the tracks part at reference frame {self.polled[d]} (level {int(self.refram[self.polled[d]][LEVEL])}) "
                      f"and do not meet again: reference {kd_ref}  here {kd_cur}; searching a re-roll", flush=True)
                fixed = base is not None and self.repair(d)
                if not fixed and base is not None and not self.is_loose(d):
                    # the enemy cannot be put back where it was: from here to the end of the level only ask that the
                    # toad's own track, the enemies' health and the hit counter are the reference's
                    self.loose = True
                    self.loose_level = int(self.refram[self.polled[d]][LEVEL])
                    self.loose_from.append(base["k"])
                    print(f"[{a.tag}] no re-roll restores the enemy's exact position at reference frame {self.polled[d]}: "
                          f"switching to the loose key (toad, enemy health, hit counter) until the level ends", flush=True)
                    if self.k > base["k"]:
                        self.restore(base, drop_later=True)     # (repair() already went back at least this far)
                    prev_lv = None
                    continue
                if not fixed:
                    stuck = d
                    print(f"[{a.tag}] STUCK at reference frame {self.polled[d]} (polled index {d}): no Select pattern in the "
                          f"last {a.window} polled frames restores the reference's track ({self.trials} tries in all)", flush=True)
                    if base is not None and self.k > base["k"]:
                        self.restore(base, drop_later=True)
                    break
                prev_lv = self.ram[LEVEL] if self.ram else None
            # the reference's inputs are used up but the game has not cut to T. Bird yet (this core's ending is longer):
            # nothing more to press, wait for the cut
            cuts = lambda: sum(1 for c in self.level_log if c["from"] == 13 and c["to"] == 254)
            if stuck is None and not ended and self.k >= self.K and cuts() < 2:
                prev = self.ram[LEVEL]
                for _ in range(2500):
                    fc, lag, isl, hx = e.cmd("capstep -").split(" ")
                    self.ram = bytes.fromhex(hx)
                    self.sent.append(())
                    self.t += 1
                    lv = self.ram[LEVEL]
                    if lv != prev:
                        self.level_log.append({"frame": self.t, "from": prev, "to": lv, "next_ref_polled_frame": None, "lag": None})
                        if prev == 13 and lv == 254 and cuts() >= 2:
                            print(f"[{a.tag}] frame {self.t}: cut to T. Bird (after the reference's inputs ran out)", flush=True)
                            break
                        prev = lv
        finally:
            done = stuck is None and (ended or self.k >= self.K)
            self.write(done)
            e.close()
        print(f"[{a.tag}] {'COMPLETE' if done else 'INCOMPLETE'}: {self.k}/{self.K} polled inputs in {self.t} frames "
              f"({self.lagn} lag), {len(self.repairs)} re-rolls ({self.trials} tries), {time.time() - self.t0:.0f}s", flush=True)
        if done and a.verify:
            self.verify()

    def verify(self):
        """The search used savestates; the result must hold without them. Replay the written input list from power-on
        on a fresh emulator (a.verify times) and compare the final RAM with this session's."""
        a = self.a
        want = sha(self.ram)
        summ_path = FIX / f"core_{a.tag}.json"
        summ = json.loads(summ_path.read_text())
        summ["verify"] = []
        for n in range(a.verify):
            e = emu_mod.BizHawk(log_name=f"fix_core_{a.tag}_verify{n + 1}.log", fields={})
            info = parse_info(e.cmd("coreinfo"))
            prev = None
            cuts = []
            ram = b""
            for i, b in enumerate(self.sent):
                fc, lag, isl, hx = e.cmd("capstep " + (",".join(b) or "-")).split(" ")
                ram = bytes.fromhex(hx)
                lv = ram[LEVEL]
                if prev == 13 and lv == 254:
                    cuts.append(i + 1)
                prev = lv
            e.close()
            got = sha(ram)
            ok = got == want and info["core_seen"].lower() == a.core.lower()
            summ["verify"].append({"replay": n + 1, "core": info["core_seen"], "sha1_at_end": got, "match": ok, "cuts_13_to_254": cuts})
            print(f"[{a.tag}] verify {n + 1}: straight replay from power-on on {info['core_seen']}: {len(self.sent)} frames, "
                  f"SHA-1 {got[:8]} {'MATCH' if ok else 'MISMATCH (session ' + want[:8] + ')'}; 13 -> 254 at {cuts} "
                  f"(the second is the cut to T. Bird)", flush=True)
        tmpj = FIX / f"core_{a.tag}.json.tmp"
        tmpj.write_text(json.dumps(summ, indent=1))
        tmpj.replace(summ_path)


def port(a):
    FIX.mkdir(parents=True, exist_ok=True)
    if a.loose_level is None:
        a.loose_level = [13]          # the Queen's exact position cannot be re-fitted (run p1 stuck on it)
    Porter(a).go()


# ------------------------------------------------------------------ compare
def load(tag):
    ram = np.memmap(FIX / f"core_{tag}.ram", dtype=np.uint8, mode="r")
    ram = ram.reshape(-1, RAM)
    meta = np.loadtxt(FIX / f"core_{tag}.meta.tsv", dtype=np.int64, delimiter="\t")
    summ = json.loads((FIX / f"core_{tag}.json").read_text())
    return ram, meta, summ


def name(addr):
    return NAMES.get(addr, "")


def first_true(mask):
    idx = np.flatnonzero(mask)
    return int(idx[0]) if len(idx) else None


def diff_bytes(ra, rb, limit=40):
    idx = np.flatnonzero(ra != rb)
    return [{"addr": f"${int(i):03X}", "name": name(int(i)), "a": int(ra[i]), "b": int(rb[i])} for i in idx[:limit]], int(len(idx))


def cmp(a):
    A, mA, sA = load(a.a)
    B, mB, sB = load(a.b)
    k = a.shift
    # B's frame f+k against A's frame f
    f_lo = max(0, -k)
    n = min(len(A) - f_lo, len(B) - (f_lo + k))
    Aw = A[f_lo:f_lo + n]
    Bw = B[f_lo + k:f_lo + k + n]
    neq = Aw != Bw
    any_diff = neq.any(axis=1)
    rng_mask = np.zeros(RAM, dtype=bool)
    rng_mask[list(RNG)] = True
    non_rng = neq[:, ~rng_mask].any(axis=1)
    rng_only = neq[:, rng_mask].any(axis=1)
    toad_addrs = [0x3FD, 0x3EE, 0x41B, 0x439, 0x493, 0x3B5, 0x51A]
    toad = neq[:, toad_addrs].any(axis=1)
    lvl = neq[:, LEVEL]
    out = {"a": a.a, "b": a.b, "shift": k, "core_a": sA["core_info"]["core_seen"], "core_b": sB["core_info"]["core_seen"],
           "frames_compared": int(n), "first_frame_compared": f_lo}
    f_any = first_true(any_diff)
    f_rng = first_true(rng_only)
    f_non = first_true(non_rng)
    f_toad = first_true(toad)
    f_lvl = first_true(lvl)
    conv = lambda i: None if i is None else i + f_lo
    out["first_any_byte"] = conv(f_any)
    out["first_rng_byte"] = conv(f_rng)
    out["first_non_rng_byte"] = conv(f_non)
    out["first_toad_byte"] = conv(f_toad)
    out["first_level_byte"] = conv(f_lvl)
    out["frames_identical"] = int((~any_diff).sum())
    out["frames_identical_but_rng"] = int((~non_rng).sum())
    # where do they finally part for good (last frame that is identical apart from the dice)?
    same = np.flatnonzero(~non_rng)
    out["last_frame_same_but_rng"] = conv(int(same[-1])) if len(same) else None
    for key, fi in (("at_first_any", f_any), ("at_first_non_rng", f_non), ("at_first_toad", f_toad)):
        if fi is not None:
            lst, cnt = diff_bytes(Aw[fi], Bw[fi])
            out[key] = {"frame_a": fi + f_lo, "frame_b": fi + f_lo + k, "bytes_differing": cnt, "bytes": lst}
    # lag: the bridge reports emu.lagcount(); per-frame lag flag in column 3
    la = mA[f_lo:f_lo + n, 3]
    lb = mB[f_lo + k:f_lo + k + n, 3]
    lag_diff = np.flatnonzero(la != lb)
    out["lag_frames_a"] = int(la.sum())
    out["lag_frames_b"] = int(lb.sum())
    out["first_lag_flag_difference"] = conv(int(lag_diff[0])) if len(lag_diff) else None
    out["lag_flag_differences"] = int(len(lag_diff))
    if f_non is not None:
        out["lag_before_first_non_rng"] = {"a": int(la[:f_non].sum()), "b": int(lb[:f_non].sum())}
    # sha1 table: every 600 frames and at each of A's level changes
    rows = []
    marks = sorted(set(list(range(600, f_lo + n, 600)) + [c["frame"] for c in sA["level_changes"]]))
    for f in marks:
        if f < f_lo or f - f_lo >= n:
            continue
        ra, rb = Aw[f - f_lo], Bw[f - f_lo]
        d = int((ra != rb).sum())
        d_non = int((ra != rb)[~rng_mask].sum())
        rows.append({"frame": f, "sha1_a": sha(ra.tobytes())[:10], "sha1_b": sha(rb.tobytes())[:10], "level_a": int(ra[LEVEL]),
                     "level_b": int(rb[LEVEL]), "bytes_differing": d, "non_rng_bytes_differing": d_non,
                     "level_change": any(c["frame"] == f for c in sA["level_changes"])})
    out["checkpoints"] = rows
    out["level_changes_a"] = sA["level_changes"]
    out["level_changes_b"] = sB["level_changes"]
    name_ = f"core_cmp_{a.a}_{a.b}" + (f"_s{k}" if k else "") + ".json"
    (FIX / name_).write_text(json.dumps(out, indent=1))
    brief = {x: out[x] for x in out if x not in ("checkpoints", "level_changes_a", "level_changes_b")}
    print(json.dumps(brief, indent=1))
    print("checkpoints (frame  sha1 A / B  level A/B  differing bytes (non-dice)):")
    shown = 0
    for r in rows:
        if r["bytes_differing"] or r["level_change"] or shown < 3:
            print(f"  {r['frame']:6d}  {r['sha1_a']} {r['sha1_b']}  {r['level_a']:3d}/{r['level_b']:3d}  "
                  f"{r['bytes_differing']:4d} ({r['non_rng_bytes_differing']}){'  <- level change' if r['level_change'] else ''}")
            shown += 1
            if shown > 40:
                print("  ..."); break
    print("wrote", FIX / name_)


def info(a):
    A, mA, sA = load(a.tag)
    print(json.dumps({k: v for k, v in sA.items() if k != "sha1_every_600"}, indent=1))
    print("frames", len(A), "lag frames", int(mA[:, 3].sum()))


# ------------------------------------------------------------------ hands-off movie
def movie(a):
    FIX.mkdir(parents=True, exist_ok=True)
    src = Path(a.movie)
    if not src.is_absolute():
        src = PROJECT / src
    mv = FIX / f"core_{a.tag}.bk2"
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(mv, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            data = zi.read(it.filename)
            if it.filename == "Header.txt" and not a.keep_header:
                lines = data.decode("utf-8").splitlines()
                lines = [("Core " + a.core) if l.startswith("Core ") else l for l in lines]
                data = ("\n".join(lines) + "\n").encode("utf-8")
            zo.writestr(it.filename, data)
    with zipfile.ZipFile(mv) as z:
        n_rows = sum(1 for l in z.read("Input Log.txt").decode().splitlines() if l.startswith("|"))
        header_core = [l for l in z.read("Header.txt").decode().splitlines() if l.startswith("Core ")]
    frames = a.frames or n_rows
    lua = FIX / "core_movie_watch.lua"
    tmp = lua.with_suffix(".lua.tmp")
    tmp.write_text(MOVIE_LUA, encoding="utf-8")
    tmp.replace(lua)
    priv = PROJECT / "emu_tmp" / f"{os.getpid()}_{uuid.uuid4().hex[:8]}"
    priv.mkdir(parents=True, exist_ok=True)
    conf = json.loads((BIZHAWK_DIR / "config.ini").read_text(encoding="utf-8-sig"))
    if "Rewind" in conf:
        conf["Rewind"]["Enabled"] = False
    conf["PreferredCores"]["NES"] = a.core
    cfg = priv / "config.ini"
    cfg.write_text(json.dumps(conf, indent=1), encoding="utf-8")
    out = FIX / f"core_{a.tag}.movie.tsv"
    if out.exists():
        out.unlink()
    args = [str(EMUHAWK), f"--config={cfg}", f"--lua={lua}", f"--userdata=frames:{frames};out:{out}", f"--movie={mv}", str(ROM)]
    print(f"[{a.tag}] movie {mv.name} ({n_rows} rows, header {header_core}), config prefers {a.core}, {frames} frames", flush=True)
    t0 = time.time()
    log = open(LOGS_DIR / f"fix_core_{a.tag}.log", "w")
    p = subprocess.Popen(args, cwd=str(BIZHAWK_DIR), stdout=log, stderr=subprocess.STDOUT)
    print(f"[{a.tag}] EmuHawk pid {p.pid}", flush=True)
    try:
        p.wait(timeout=a.timeout)
    except subprocess.TimeoutExpired:
        print(f"[{a.tag}] timeout after {a.timeout}s: killing my own EmuHawk pid {p.pid}")
        p.kill()
    log.close()
    print(f"[{a.tag}] finished in {time.time() - t0:.0f}s")
    if out.exists():
        lines = out.read_text().splitlines()
        print(lines[0] if lines else "(empty)")
        prev = None
        for l in lines[1:]:
            fc, lv, lag, h = l.split("\t")
            if lv != prev:
                print(f"  movie frame {fc}: level byte {lv}  lag {lag}  sha256 {h[:12]}")
                prev = lv
        print("  last:", lines[-1][:60])
    else:
        print("no output written (see logs/fix_core_%s.log)" % a.tag)


def pcmp(a):
    """Compare two captures by POLLED frame (the k-th frame on which the game read the controller in each): the
    comparison that is fair when the two cores take different numbers of lag frames. Table at every level change of A
    and every 600 frames of A: B's frame, the offset, RAM SHA-1 of both, bytes differing (dice/idle/stack aside), and
    whether the run-relevant key (toad, tracked enemies, level, hit counter) is the same."""
    A, mA, sA = load(a.a)
    B, mB, sB = load(a.b)
    pa = [f for f in range(a.first_poll, len(A)) if mA[f, 3] == 0]
    pb = [f for f in range(a.first_poll, len(B)) if mB[f, 3] == 0]
    n = min(len(pa), len(pb))
    mask = soft_mask()
    mask[0x740:0x760] = False                     # a buffer the sound engine fills: follows the idle loop too
    marks = sorted(set(list(range(600, len(A), 600)) + [c["frame"] for c in sA["level_changes"]]))
    lvl_change = {c["frame"]: c for c in sA["level_changes"]}
    import bisect
    rows = []
    key_same = soft_same = 0
    first_key = first_soft = None
    for k in range(n):
        fa, fb = pa[k], pb[k]
        ra, rb = A[fa], B[fb]
        ks = gkey(ra, True) == gkey(rb, True)
        d = int(((ra != rb) & mask).sum())
        key_same += ks
        soft_same += d == 0
        if not ks and first_key is None:
            first_key = {"frame_a": fa, "frame_b": fb}
        if d and first_soft is None:
            lst, cnt = diff_bytes(ra, rb)
            first_soft = {"frame_a": fa, "frame_b": fb, "bytes": [x for x in lst if x["addr"] not in ("$025", "$026", "$027", "$028", "$075")][:12]}
    for f in marks:
        k = bisect.bisect_left(pa, f)             # the first polled frame at or after the mark
        if k >= n:
            break
        fa, fb = pa[k], pb[k]
        ra, rb = A[fa], B[fb]
        rows.append({"mark": f, "level_change": f"{lvl_change[f]['from']}->{lvl_change[f]['to']}" if f in lvl_change else "",
                     "frame_a": fa, "frame_b": fb, "offset": fb - fa, "level_a": int(ra[LEVEL]), "level_b": int(rb[LEVEL]),
                     "sha1_a": sha(ra.tobytes())[:10], "sha1_b": sha(rb.tobytes())[:10], "identical": bool((ra == rb).all()),
                     "bytes_differing_dice_aside": int(((ra != rb) & mask).sum()),
                     "key_same": gkey(ra, True) == gkey(rb, True), "lag_a": int(mA[:fa + 1, 3].sum()), "lag_b": int(mB[:fb + 1, 3].sum())})
    out = {"a": a.a, "b": a.b, "core_a": sA["core_info"]["core_seen"], "core_b": sB["core_info"]["core_seen"],
           "polled_a": len(pa), "polled_b": len(pb), "polled_compared": n, "polled_key_same": int(key_same),
           "polled_same_dice_aside": int(soft_same), "first_key_difference": first_key, "first_difference_dice_aside": first_soft,
           "level_changes_a": sA["level_changes"], "level_changes_b": sB["level_changes"], "rows": rows}
    (FIX / f"core_pcmp_{a.a}_{a.b}.json").write_text(json.dumps(out, indent=1))
    lines = [f"| mark (frame of {a.a}) | level change | {out['core_a']} frame | {out['core_b']} frame | offset | SHA-1 {out['core_a']} | "
             f"SHA-1 {out['core_b']} | bytes differing (dice aside) | toad/enemy key |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['mark']} | {r['level_change']} | {r['frame_a']} | {r['frame_b']} | {r['offset']:+d} | {r['sha1_a']} | {r['sha1_b']} | "
                     f"{'identical RAM' if r['identical'] else r['bytes_differing_dice_aside']} | {'same' if r['key_same'] else 'DIFFERENT'} |")
    (FIX / f"core_pcmp_{a.a}_{a.b}.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "level_changes_a", "level_changes_b")}, indent=1))
    print(f"{len(rows)} marks; key same at {sum(r['key_same'] for r in rows)}; offsets seen {sorted(set(r['offset'] for r in rows))}")
    print("wrote", FIX / f"core_pcmp_{a.a}_{a.b}.md")


def bk2(a):
    """Write a capture's input list as a BizHawk movie whose header names the core it was made for. One empty lead-in
    frame, like the published movie: hands-off playback applies row n+1 where the bridge applied input n."""
    summ = json.loads((FIX / f"core_{a.tag}.json").read_text())
    rows = read_inputs(PROJECT / summ["inputs"])
    core = a.core or summ["core_info"]["core_seen"]
    order = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
    mn = {"Up": "U", "Down": "D", "Left": "L", "Right": "R", "Select": "s", "Start": "S", "B": "B", "A": "A"}
    data = Path(ROM).read_bytes()
    if data[:4] == b"NES\x1a":
        data = data[16:]
    header = "\n".join(["MovieVersion BizHawk v2.0.0", "Author Claude (Anthropic), via Claude Code",
                        "emuVersion Version 2.11.1", "OriginalEmuVersion Version 2.11.1", "Platform NES", "SystemID NES",
                        "GameName Battletoads", f"SHA1 {hashlib.sha1(data).hexdigest().upper()}", "rerecordCount 0",
                        f"Core {core}"]) + "\n"
    frames = [()] * a.lead + rows
    log = ("[Input]\nLogKey:#Reset|Power|#P1 Up|P1 Down|P1 Left|P1 Right|P1 Select|P1 Start|P1 B|P1 A|\n" +
           "\n".join("|..|" + "".join(mn[b] if b in f else "." for b in order) + "|" for f in frames) + "\n[/Input]\n")
    out = FIX / f"core_{a.tag}_{core}.bk2"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Header.txt", header)
        z.writestr("Input Log.txt", log)
        z.writestr("Comments.txt", f"core check: {summ['inputs']} for the {core} core, {len(frames)} frames from power-on "
                                   f"({a.lead} empty lead-in). A test movie, not a timed claim.\n")
        z.writestr("Subtitles.txt", "")
    print("wrote", out, len(frames), "frames, Core", core)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("tag")
    r.add_argument("--core", default=None)
    r.add_argument("--lead", type=int, default=0)
    r.add_argument("--inputs", default="logs/up14.inputs.txt")
    r.add_argument("--tail", type=int, default=800)
    r.add_argument("--stop", type=int, default=0)
    c = sub.add_parser("cmp")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--shift", type=int, default=0)
    m = sub.add_parser("movie")
    m.add_argument("tag")
    m.add_argument("movie")
    m.add_argument("--core", default="NesHawk")
    m.add_argument("--frames", type=int, default=0)
    m.add_argument("--keep-header", action="store_true")
    m.add_argument("--timeout", type=int, default=3600)
    i = sub.add_parser("info")
    i.add_argument("tag")
    el = sub.add_parser("elastic")
    el.add_argument("tag")
    el.add_argument("--ref", default="q")
    el.add_argument("--core", default="NesHawk")
    el.add_argument("--patience", type=int, default=900)      # polled frames in a row that differ = diverged
    el.add_argument("--after", type=int, default=1500)        # keep going this long after the divergence
    el.add_argument("--max-frames", type=int, default=60000)
    el.add_argument("--all-bytes", dest="key_only", action="store_false")   # diverge on any byte, not just toad/camera
    el.add_argument("--first-poll", type=int, default=100)    # ignore reference "polls" before this frame (boot artefact)
    po = sub.add_parser("port")
    po.add_argument("tag")
    po.add_argument("--ref", default="q")
    po.add_argument("--core", default="NesHawk")
    po.add_argument("--first-poll", type=int, default=100)
    po.add_argument("--every", type=int, default=6)           # a savestate every N polled frames
    po.add_argument("--ring", type=int, default=70)           # savestates kept
    po.add_argument("--window", type=int, default=180)        # how far back a Select may go (rngfit's W)
    po.add_argument("--hold", type=int, default=12)           # polled frames the track must hold past the break (rngfit's M)
    po.add_argument("--look", type=int, default=900)          # how long to wait for the tracks to meet again by themselves
    po.add_argument("--rejoin", type=int, default=60)         # ... and how long they must then stay together
    po.add_argument("--random-tries", type=int, default=1200)
    po.add_argument("--strict-random", type=int, default=300)  # ... of them at most this many while the enemy's exact position is in the key
    po.add_argument("--max-frames", type=int, default=70000)
    po.add_argument("--verbose", action="store_true")
    po.add_argument("--mods-from", default=None)              # start with the Select toggles an earlier port run found
    po.add_argument("--best-of", type=int, default=2)         # compare this many working re-rolls, keep the one that holds longest
    po.add_argument("--extra", type=int, default=90)          # ... measured this many polled frames past --hold
    po.add_argument("--loose-level", type=int, action="append", default=None)   # level bytes whose enemies' positions are not in the key (default: 13, the Queen)
    po.add_argument("--verify", type=int, default=2)          # straight replays from power-on of the result (0 = none)
    po.add_argument("--end-steer", type=float, default=0)     # seconds of track END's ending search on this core at the last hit (0 = feed the reference's own ending)
    bk = sub.add_parser("bk2")
    bk.add_argument("tag")
    bk.add_argument("--core", default=None)
    bk.add_argument("--lead", type=int, default=1)
    pc = sub.add_parser("pcmp")
    pc.add_argument("a")
    pc.add_argument("b")
    pc.add_argument("--first-poll", type=int, default=100)
    a = ap.parse_args()
    {"run": run, "cmp": cmp, "movie": movie, "info": info, "elastic": elastic, "port": port, "bk2": bk2, "pcmp": pcmp}[a.cmd](a)
