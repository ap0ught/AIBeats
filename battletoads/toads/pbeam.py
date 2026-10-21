"""Parallel beam search with random playouts. Brute force with a short memory of the future.

Every STEP frames, each state in the beam tries every macro. A child is scored by its own RAM plus the best of R
random playouts of H frames after it, so a punch that sets up a kill 60 frames later is rewarded now, without the
search having to know what an enemy's health looks like in memory (it doesn't: we looked and didn't find it).

Beam states live in files (states/pbeam/<run>/n<k>.State) so any of the scout emulators can expand any node.
"""
from __future__ import annotations

import json
import random
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from .emulator import BizHawk, STATES_DIR
from .beam import MACROS, read_info, score, run_macro

DIRS = [m[0] for m in MACROS]
TIME_W = 3.0            # points per frame: a kill 100 frames sooner is worth 300


@dataclass
class Node:
    state: str                     # savestate name relative to STATES_DIR
    inputs: list = field(default_factory=list)
    info: dict = field(default_factory=dict)
    value: float = 0.0


def playout(emu, rng, frames, base, node_info):
    """Random macros for `frames` frames; return the best score seen at any macro boundary."""
    best, kills, alive = -1e9, node_info["kills"], node_info["alive"]
    n = 0
    while n < frames:
        m = MACROS[rng.randrange(len(MACROS))]
        k = rng.choice([8, 12, 16])
        run_macro(emu, m, k)
        n += k
        info = read_info(emu.ram_all())
        kills += max(0, alive - info["alive"])
        alive = info["alive"]
        best = max(best, score(info, base, kills))
    return best


def search(scouts: list[BizHawk], bookmark: str, run: str, steps=80, width=4, step=16, rollouts=2, horizon=64,
           stop=None, log=print, gamma=0.6):
    d = STATES_DIR / "pbeam" / run
    d.mkdir(parents=True, exist_ok=True)
    emu0 = scouts[0]
    emu0.load(bookmark)
    base = read_info(emu0.ram_all())
    base["kills"] = 0
    base["foe_hp0"] = base["foe_hp"]
    base["warp0"] = base["warp"]
    root = Node(bookmark, [], dict(base), 0.0)
    beam_nodes = [root]
    lock = threading.Lock()
    counter = {"n": 0}
    t0 = time.time()
    history = []
    for k in range(steps):
        tasks = [(pi, mi) for pi in range(len(beam_nodes)) for mi in range(len(MACROS))]
        results = [None] * len(tasks)
        nxt = {"i": 0}

        def work(emu):
            while True:
                with lock:
                    i = nxt["i"]
                    if i >= len(tasks):
                        return
                    nxt["i"] += 1
                pi, mi = tasks[i]
                parent = beam_nodes[pi]
                emu.load(parent.state)
                ins = run_macro(emu, MACROS[mi], step)
                info = read_info(emu.ram_all())
                kills = parent.info["kills"] + max(0, parent.info["alive"] - info["alive"]) if info["foe_hp"] < parent.info["foe_hp"] or info["alive"] < parent.info["alive"] and info["foe_hp"] <= parent.info["foe_hp"] else parent.info["kills"]
                info["kills"] = kills
                own = score(info, base, kills)
                sid = emu.msave()
                fut = own
                for r in range(rollouts):
                    emu.mload(sid)
                    rng = random.Random(hash((k, pi, mi, r)) & 0xFFFFFFFF)
                    fut = max(fut, playout(emu, rng, horizon, base, info))
                emu.mfree(sid)
                frames = len(parent.inputs) + len(ins)
                results[i] = (pi, mi, ins, info, own + gamma * (fut - own) - TIME_W * frames)

        threads = [threading.Thread(target=work, args=(e,)) for e in scouts]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        def parent_inputs(pi):
            return beam_nodes[pi].inputs
        results = [r for r in results if r]
        results.sort(key=lambda r: -r[4])
        keep, seen = [], set()
        for pi, mi, ins, info, val in results:
            key = (info["camera"] // 4, info["x"] // 8, info["alive"], info["hp"], info["foe_hp"], info["level"], info["warp"] // 16, len(parent_inputs(pi)) // 24)
            if key in seen:
                continue
            seen.add(key)
            keep.append((pi, mi, ins, info, val))
            if len(keep) >= width:
                break
        new = []
        for pi, mi, ins, info, val in keep:            # materialize survivors as files
            parent = beam_nodes[pi]
            emu0.load(parent.state)
            run_macro(emu0, MACROS[mi], step)
            counter["n"] += 1
            name = f"pbeam/{run}/n{counter['n']}"
            emu0.save(name)
            new.append(Node(name, parent.inputs + ins, info, val))
        beam_nodes = new
        best = beam_nodes[0]
        history.append({"step": k + 1, "frames": len(best.inputs), "value": round(best.value, 1), **best.info})
        log(f"  step {k + 1:3d}  frames {len(best.inputs):5d}  value {best.value:8.1f}  {json.dumps(best.info)}  "
            f"{time.time() - t0:.0f}s")
        if stop and stop(best.info):
            break
    return beam_nodes[0], history
