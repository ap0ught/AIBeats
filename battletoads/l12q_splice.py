"""Compose the L12q piece (boot + chase + join + walker fight) and splice it into L12r (2026-10-06)."""
import json, subprocess, sys
boot = json.load(open("knowledge/l12_boot_w12.json")); chase = json.load(open("knowledge/l12_chase.json")); rj = json.load(open("knowledge/rj_chase.json"))
wq = json.load(open("knowledge/fight_wq.json"))
assert rj["b"] == wq["a"] == 6786, (rj["b"], wq["a"])
ins = list(boot["inputs"]) + list(chase["inputs"]) + list(rj["inputs"]) + list(wq["inputs"])
piece = {"a": 6184, "b": wq["b"], "inputs": ins, "note": "big boot 6311, oncoming-platform launch one lap early, join 6786, walker fight re-done, join " + str(wq["b"])}
json.dump(piece, open("knowledge/piece_L12q.json", "w"))
print("piece: a 6184 b", wq["b"], "inputs", len(ins), "replaces", wq["b"] - 6184, "saves", wq["b"] - 6184 - len(ins), flush=True)
sys.exit(subprocess.run([sys.executable, "-u", "splice.py", "L12r", "knowledge/piece_L12q.json", "L12q"]).returncode)
