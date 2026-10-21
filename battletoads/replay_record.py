"""Replay a full input list from POWER-ON with A/V recording and the per-frame trace (for the panel).
python replay_record.py <session name> <inputs.txt>"""
import sys, hashlib
from toads.emulator import BizHawk, LOGS_DIR
name, src = sys.argv[1], sys.argv[2]
lines = [l for l in open(src).read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name=f"{name}.log", record=name)
notes = {}
for l in (open(src.replace(".inputs.txt", ".events.txt")).read().splitlines() if src.endswith(".inputs.txt") else []):
    f, _, t = l.partition("\t"); notes.setdefault(int(f), []).append(t)
for i, l in enumerate(lines):
    for t in notes.get(i + 1, []): e.note(t)
    e.step(tuple(x for x in l.split("+") if x), 1)
h = hashlib.sha1(e.ram_all()).hexdigest()
print("frames", len(lines), "final", e.state(), "ram sha1", h)
e.close()
