"""Chain A: the refit chain behind a new Level 8 (rngfit of Levels 9, 10, 11, 12), one level after the other.

    python u16a_chain.py <entry bookmark of Level 9> <tag> <first level> <last level>
        e.g.  python u16a_chain.py A8_end0 "" 9 12     -> A9, A10, A11, A12 (logs/pbeam_A<n><tag>.json, bookmarks A<n><tag>_end0)
        level 9 = L9heli_c2, 10 = L9heli_c2L10, 11 = L9heli_c2L11s (RNGFIT_IDS=7b), 12 = L12h (RNGFIT_IDS=5c,62)
        a later start (e.g. 11 12) takes A<first-1><tag>_end0 as its entry unless <entry bookmark> is given as that
    Each step runs u16a_rngfit.py (chain A's copy of rngfit.py: A,B page mash, page dice, the HEAD fix) with explicit output
    names - NOT fitchain.py, which derives the level and the output name from the segment name and gets both wrong for
    names like L9heli_c2L11s.  Fit logs: logs/fix/u16a_fit_A<n><tag>.txt; one summary block per step is appended to
    logs/fix/u16a_chain.txt.  Stops at the first step that sticks (exit code 1).

(This file was rewritten 2026-10-10 02:55 after the first version was overwritten by mistake; same command line and outputs.)
"""
import json
import os
import subprocess
import sys
import time

from toads.emulator import LOGS_DIR

STEPS = {9: ("L9heli_c2", ""), 10: ("L9heli_c2L10", ""), 11: ("L9heli_c2L11s", "7b"), 12: ("L12h", "5c,62")}


def main(entry, tag, first, last):
    summ = open(LOGS_DIR / "fix" / "u16a_chain.txt", "a", encoding="utf-8")

    def say(s):
        print(s, flush=True)
        summ.write(s + "\n"); summ.flush()

    for n in range(first, last + 1):
        seg, ids = STEPS[n]
        out = f"A{n}{tag}"
        log = LOGS_DIR / "fix" / f"u16a_fit_{out}.txt"
        env = dict(os.environ, RNGFIT_IDS=ids)
        env.pop("TOADS_CORE", None)
        t0 = time.time()
        with open(log, "w") as f:
            rc = subprocess.run([sys.executable, "u16a_rngfit.py", seg, entry, out], env=env, stdout=f, stderr=subprocess.STDOUT).returncode
        lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
        if rc:
            say(f"step {n}: {seg} from {entry} -> {out}: STUCK (exit {rc}), {time.time() - t0:.0f}s; RNGFIT_IDS={ids!r}")
            for l in lines[-6:]:
                say("     " + l.strip()[:300])
            return 1
        d = json.load(open(LOGS_DIR / f"pbeam_{out}.json"))
        old = len(json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))["inputs"])
        rr = [r[0] for r in d.get("rerolls", [])]
        say(f"step {n}: {seg} ({old}) from {entry} -> {out}: {len(d['inputs'])} frames ({len(d['inputs']) - old:+d}), {len(rr)} re-rolls {rr}, "
            f"{time.time() - t0:.0f}s; RNGFIT_IDS={ids!r}")
        for l in lines:
            if l.startswith("  ") and "head:" not in l:
                say("   " + l.rstrip()[:300])
        entry = out + "_end0"
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])))
