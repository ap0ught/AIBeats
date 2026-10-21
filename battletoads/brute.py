"""Pure brute force: many random input sequences from one bookmark, spread across several emulators.

Each attempt is a list of macros (a button combo held for a random number of frames). Nothing about the game is
assumed except the button names. Every attempt's inputs, final RAM, a few RAM samples, and its last screenshot are
kept, so afterwards ramscan can ask what the attempts that got further have in common.

    python brute.py <name> <bookmark> [attempts] [frames] [scouts]
"""
from __future__ import annotations

import json
import random
import shutil
import sys
import threading
import time

import numpy as np

from toads.emulator import BizHawk, LOGS_DIR, SHOTS_DIR
from toads import tokens

DIRS = [(), ("Right",), ("Left",), ("Up",), ("Down",), ("Right", "Up"), ("Right", "Down"), ("Left", "Up"), ("Left", "Down")]
ACTS = [(), (), ("B",), ("A",)]


def random_plan(rng: random.Random, frames: int):
    plan, n = [], 0
    while n < frames:
        d = rng.choice(DIRS)
        a = rng.choice(ACTS)
        hold = rng.choice([2, 4, 6, 8, 12, 16, 24])
        if a:                                 # a press needs an edge: hold it briefly, then release it
            plan.append((d + a, 2))
            plan.append((d, max(hold - 2, 2)))
        else:
            plan.append((d, hold))
        n += hold
    return plan


def run(name: str, bookmark: str, attempts: int = 120, frames: int = 1500, scouts: int = 6, sample_every: int = 30):
    out = LOGS_DIR / "brute" / name
    shots = SHOTS_DIR / "brute" / name
    out.mkdir(parents=True, exist_ok=True)
    shots.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    state = {"next": 0, "done": 0}
    t0 = time.time()

    def work(k):
        emu = BizHawk(log_name=f"brute_{name}_{k}.log")
        try:
            while True:
                with lock:
                    i = state["next"]
                    if i >= attempts:
                        return
                    state["next"] += 1
                rng = random.Random(10_000 + i)
                emu.load(bookmark)
                plan = random_plan(rng, frames)
                samples, inputs = [], []
                f = 0
                for btn, n in plan:
                    for _ in range(n):
                        emu.step(btn, 1)
                        inputs.append("+".join(btn))
                        f += 1
                        if f % sample_every == 0:
                            samples.append(np.frombuffer(emu.ram_all(), dtype=np.uint8))
                np.save(out / f"a{i:04d}.npy", np.stack(samples))
                (out / f"a{i:04d}.json").write_text(json.dumps({"seed": 10_000 + i, "inputs": inputs,
                                                                  "final": emu.state()}))
                shutil.copyfile(emu.screenshot(f"_brute_{name}_{k}"), shots / f"a{i:04d}.png")
                with lock:
                    state["done"] += 1
                    if state["done"] % 10 == 0:
                        print(f"  {state['done']}/{attempts} attempts, {time.time() - t0:.0f}s", flush=True)
        finally:
            emu.close()

    threads = [threading.Thread(target=work, args=(k,)) for k in range(scouts)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"{name}: {attempts} attempts x {frames} frames in {time.time() - t0:.0f}s")
    tokens.mark(f"brute {name}", {"attempts": attempts, "frames": frames})


if __name__ == "__main__":
    a = sys.argv
    run(a[1], a[2], int(a[3]) if len(a) > 3 else 120, int(a[4]) if len(a) > 4 else 1500, int(a[5]) if len(a) > 5 else 6)
