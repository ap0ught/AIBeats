"""Re-fit a chain of segments onto a new upstream route (2026-10-02; replaces fitchain.sh).

For each segment: (1) entry scan - the entry bookmark is the frame the toad is set down in the new level, the old
inputs were made `slack` idle frames later; find the fewest idle frames after which the old track still holds
(rngfit.py --scan); (2) fit with that wait (Select re-rolls, wait repairs, briefing-page mash at the end);
(3) if that sticks, fit again with the full slack (the old run's own entry frame).

    python fitchain.py <entry bookmark (toad set down)> <slack> <tag> <segment> [...]
        -> logs/pbeam_<segment minus last letter><tag>.json each, logs/fit_<segment>_<tag>.txt; prints one line each
"""
import json
import os
import re
import subprocess
import sys

from toads.emulator import LOGS_DIR

IDS = {"L8": "7d", "L11": "7b", "L12": "5c,62"}
BYTES = {"L13": "586"}


def run(args, env, log):
    with open(log, "a") as f:
        return subprocess.run([sys.executable, "rngfit.py"] + args, env=env, stdout=f, stderr=subprocess.STDOUT).returncode


def main(entry, slack, tag, segs):
    slack = int(slack)
    for seg in segs:
        lvl = re.match(r"L\d+", seg).group(0)
        out = seg[:-1] + tag
        env = dict(os.environ, RNGFIT_IDS=IDS.get(lvl, ""), RNGFIT_BYTES=BYTES.get(lvl, ""))
        log = str(LOGS_DIR / f"fit_{seg}_{tag}.txt")
        open(log, "w").close()
        k = 0
        if slack:
            run(["--scan", seg, entry, str(slack)], env, log)
            m = re.findall(r"SCAN k=(\d+)", open(log).read())
            k = int(m[-1]) if m else slack
        rc = run([seg, entry, out], dict(env, RNGFIT_ENTRYWAIT=str(k)), log)
        if rc and k != slack:
            print(f"{seg}: stuck with {k} idle frames at the entry, trying the full {slack}", flush=True)
            k = slack
            rc = run([seg, entry, out], dict(env, RNGFIT_ENTRYWAIT=str(k)), log)
        last = open(log).read().strip().splitlines()[-1][:200]
        if rc:
            print(f"{seg} STUCK: {last}", flush=True)
            return 1
        d = json.load(open(LOGS_DIR / f"pbeam_{out}.json"))
        print(f"{seg} -> {out}: {len(d['inputs'])} frames, entry wait {k} of {slack}; {last[-90:]}", flush=True)
        entry, slack = out + "_end0", d.get("slack", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]))
