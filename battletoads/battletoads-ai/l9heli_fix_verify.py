"""From POWER-ON: up14's inputs up to Level 9, then the new chain (the new Level 9 line and the re-fitted Levels 10-13), then a plain
ending (nothing, one A on the first frame the Queen's speech takes it, nothing) up to the cut to Professor T. Bird.   (2026-10-10)
    python l9heli_fix_verify.py <out tag> <L9 segment> <L10> <L11> <L12> <L13>          (segment = logs/pbeam_<name>.json)
Prints the same marks as assemble.py (clock start = the landing in Level 1; run end = the SECOND level byte 13 -> 254) and writes the
complete input list to logs/fix/heli_route_<tag>.inputs.txt.  Nothing else is written."""
import hashlib, json, sys
from toads.emulator import BizHawk, LOGS_DIR
from l9heli_fix_lib import OFF, up14_inputs, bt, banned
TAG = sys.argv[1]; SEGS = sys.argv[2:]
old = [b.replace(",", "+") for b in up14_inputs()]
ins = old[:OFF]
marks = [("up14 unchanged (Levels 1-8)", 1)]
for n in SEGS:
    marks.append((n, len(ins) + 1)); ins += json.load(open(LOGS_DIR / f"pbeam_{n}.json"))["inputs"]
print("inputs:", len(ins), "(up14:", len(old), ") segment starts:", marks, "| banned presses:", sum(1 for b in ins if banned(b)), flush=True)
(LOGS_DIR / "fix" / f"heli_route_{TAG}.inputs.txt").write_text(f"# frames={len(ins)}\n" + "\n".join(ins) + "\n")
e = BizHawk(log_name=f"l9heli_fix_verify_{TAG}.log")
t_start = None; prev = None; prev_lv = None; cuts = []; changes = []
for i, b in enumerate(ins):
    s = e.step(bt(b), 1)
    if t_start is None and s.level == 1 and prev == 5 and s.anim == 4: t_start = i + 1
    prev = s.anim
    if prev_lv is not None and s.level != prev_lv and s.level not in (254, 255) : changes.append((i + 1, s.level))
    if prev_lv == 13 and s.level == 254: cuts.append(i + 1)
    prev_lv = s.level
m = e.ram(0, 0x800); sha = hashlib.sha1(e.ram_all()).hexdigest()
print(f"after the last input ({len(ins)}): clock start {t_start}; level entries {changes}; 13->254 cuts {cuts}; level {m[0x10]} hp {m[0x51A]} lives {m[0x11]}; RAM sha1 {sha[:8]}", flush=True)
if len(cuts) >= 2 and t_start:
    run = (cuts[1] - t_start) / 60.0988
    print(f"the inputs contain the ending: cut to Professor T. Bird on frame {cuts[1]} -> RUN TIME {int(run // 60)}:{run % 60:05.2f} = {cuts[1] - t_start} frames "
          f"(record 12:29.25 = 45,029 frames)", flush=True)
    e.close(); sys.exit(0)
# plain ending: the first frame on which a new A press returns to the tower, then nothing
base = e.msave(); n0 = len(ins); best = None
for n in range(1, 40):
    e.mload(base); lv = None
    for j in range(n - 1): e.step((), 1)
    s = e.step(("A",), 1); lv = s.level
    for j in range(3):
        if lv == 13: break
        lv = e.step((), 1).level
    if lv == 13: best = n; break
print("the speech takes a new A press on frame", n0 + (best or 0), f"({best} frames after the last input)", flush=True)
if best:
    e.mload(base)
    for j in range(best - 1): e.step((), 1)
    s = e.step(("A",), 1); f = n0 + best; prev_lv = s.level; tb = None
    for j in range(900):
        s = e.step((), 1); f += 1
        if prev_lv == 13 and s.level == 254: tb = f; break
        prev_lv = s.level
    if tb and t_start:
        run = (tb - t_start) / 60.0988
        print(f"cut to Professor T. Bird on frame {tb} -> RUN TIME {int(run // 60)}:{run % 60:05.2f} = {tb - t_start} frames (record 12:29.25 = 45,029 frames); "
              f"up14 with the same plain ending: 47,253 -> {47253 - tb} frames sooner", flush=True)
    else: print("no T. Bird cut within 900 frames", flush=True)
e.close()
