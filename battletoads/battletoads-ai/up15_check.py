"""Own check of an assembled route (2026-10-10, the timing fix): no emulator, only the files assemble.py left behind.

    python up15_check.py <route> <segment>...        -> logs/fix/<route>_check.txt   (also printed)

1. rebuilds the input list from the intro + logs/pbeam_<segment>.json exactly like assemble.build and compares it with
   logs/<route>.inputs.txt (the list the recorder actually replayed, comma format);
2. banned presses: Left+Right or Up+Down on one frame, any button that is not one of the 8 on controller 1, Start anywhere
   after the title (listed with its segment: the Level 4 -> 6 warp page is a legal press; in the ENDING it would pause);
3. reads logs/<route>.trace.txt (one line per input: number, buttons, RAM fields after that frame) and reports the
   landing (level 1, anim 5 -> 4 = the clock start), every level-byte change, the Queen's last hit (slot-3 id 126 -> 70),
   both 13 -> 254 cuts (Queen's speech, Professor T. Bird), the toad's lives and health through Level 13 and the ending,
   and what was pressed after the last hit;
4. the time on the leaderboard's terms: (T. Bird cut - landing) / 60.0988, against 749.25 s (cut <= 47102 for a landing
   on 2074; 47040 = one second under).
"""
import json
import sys

from toads.emulator import LOGS_DIR
import assemble

route, segs = sys.argv[1], sys.argv[2:]
BUTTONS = {"Up", "Down", "Left", "Right", "Select", "Start", "B", "A"}
FPS = 60.0988
RECORD_S = 749.25
out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


# 1. the list ---------------------------------------------------------------------------------------------------------
ins, bounds = [], []
for b, n, _ in assemble.INTRO:
    ins += [b] * n
intro_n = len(ins)
for name in segs:
    j = json.loads((LOGS_DIR / f"pbeam_{name}.json").read_text())
    bounds.append((name, len(ins) + 1, len(j["inputs"])))
    ins += j["inputs"]
P(f"== check {route}: {' '.join(segs)}")
P(f"{len(ins)} inputs = intro {intro_n} + " + " + ".join(f"{n} {k}" for n, _, k in bounds))
P("segment first inputs: " + ", ".join(f"{n} {a}" for n, a, _ in bounds))
norm = lambda l: tuple(sorted(x for x in l.replace(",", "+").split("+") if x))
rec = [l for l in (LOGS_DIR / f"{route}.inputs.txt").read_text(encoding="utf-8").split("\n")[1:]]
if rec and rec[-1] == "":
    rec.pop()
same = len(rec) == len(ins) and all(norm(a) == norm(b) for a, b in zip(rec, ins))
P(f"logs/{route}.inputs.txt: {len(rec)} lines, {'IDENTICAL to' if same else 'DIFFERENT from'} the list built from the segments")


def seg_of(f):
    if f <= intro_n:
        return "intro"
    for n, a, k in bounds:
        if a <= f < a + k:
            return n
    return "?"


# 2. banned presses ---------------------------------------------------------------------------------------------------
lr = [i + 1 for i, l in enumerate(ins) if {"Left", "Right"} <= set(norm(l))]
ud = [i + 1 for i, l in enumerate(ins) if {"Up", "Down"} <= set(norm(l))]
unk = [(i + 1, l) for i, l in enumerate(ins) if set(norm(l)) - BUTTONS]
start = [i + 1 for i, l in enumerate(ins) if "Start" in norm(l)]
start_after = [f for f in start if f > 1174]
P(f"Left+Right frames: {len(lr)} {lr[:10]}   Up+Down frames: {len(ud)} {ud[:10]}   unknown buttons: {len(unk)} {unk[:5]}")
P(f"Start frames: {len(start)} in all; title screen {start[0] if start else None}..{max(f for f in start if f <= 1174) if start else None}; "
  f"after the title {len(start_after)}: " + ", ".join(f"{f} ({seg_of(f)})" for f in start_after))
P("controller 2: the input list has one pad's buttons per frame and bridge.lua sets controller 1 only")

# 3. the trace --------------------------------------------------------------------------------------------------------
rows = []
with open(LOGS_DIR / f"{route}.trace.txt", encoding="utf-8") as fh:
    for line in fh:
        p = line.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        d = {}
        for tok in p[2].split():
            k, _, v = tok.partition("=")
            d[k] = int(v)
        rows.append((int(p[0]), p[1], d))
P(f"trace: {len(rows)} lines, first input {rows[0][0]}, last input {rows[-1][0]}")
tr_same = len(rows) == len(ins) and all(norm(r[1]) == norm(b) for r, b in zip(rows, ins))
P(f"trace buttons {'IDENTICAL to' if tr_same else 'DIFFERENT from'} the built list")
landing, prev_an, prev_lv, cuts, changes = None, None, None, [], []
last_hit, prev_id3 = None, None
lives_ch, prev_lives = [], None
l13_first = None
for n, b, d in rows:
    if landing is None and d["level"] == 1 and prev_an == 5 and d["anim"] == 4:
        landing = n
    prev_an = d["anim"]
    if d["level"] != prev_lv:
        changes.append((n, prev_lv, d["level"]))
        if prev_lv == 13 and d["level"] == 254:
            cuts.append(n)
        if d["level"] == 13 and l13_first is None:
            l13_first = n
        prev_lv = d["level"]
    if l13_first and d["level"] == 13 and prev_id3 == 126 and d["id3"] == 70:
        last_hit = n
    prev_id3 = d["id3"]
    if d["lives"] != prev_lives:
        lives_ch.append((n, prev_lives, d["lives"], d["level"]))
        prev_lives = d["lives"]
P("level-byte changes (input number: from -> to), levels only: " +
  ", ".join(f"{n}: {a}->{b}" for n, a, b in changes if b not in (254, 255)))
P("lives changes (input, from -> to, level byte): " + ", ".join(f"{n}: {a}->{b} (lv {lv})" for n, a, b, lv in lives_ch))
P(f"landing (clock start) at input {landing}")
P(f"Level 13 from input {l13_first}; Queen's last hit (id 126 -> 70) at input {last_hit}; 13 -> 254 cuts at {cuts}")
if l13_first:
    seg13 = [(n, b, d) for n, b, d in rows if n >= l13_first + 12]
    hp13 = [(d["hp"], n) for n, b, d in seg13 if d["level"] == 13]
    P(f"toad health while the level byte is 13 (from input {l13_first + 12}): min {min(hp13)[0]} (at {min(hp13)[1]}), "
      f"max {max(hp13)[0]}; lives {sorted(set(d['lives'] for n, b, d in seg13))}")
if last_hit:
    tail = [(n, b) for n, b, d in rows if n > last_hit and b]
    kinds = {}
    for n, b in tail:
        kinds.setdefault("+".join(norm(b)), []).append(n)
    P(f"pressed after the last hit ({len(tail)} frames with a button): " +
      "; ".join(f"{k} x{len(v)} [{v[0]}..{v[-1]}]" for k, v in sorted(kinds.items(), key=lambda kv: kv[1][0])))
    P(f"Start after the last hit: {sum(1 for n, b in tail if 'Start' in norm(b))}")
    if len(cuts) > 1:
        P(f"ending: last hit -> Queen's speech cut {cuts[0] - last_hit}, -> T. Bird cut {cuts[1] - last_hit} frames "
          f"(up14 plain 1168, best known 1071)")

# 4. the time ---------------------------------------------------------------------------------------------------------
ok = False
if landing and len(cuts) > 1:
    tb = cuts[1]
    t = (tb - landing) / FPS
    lim = landing + RECORD_S * FPS                      # cut frame equal to the record
    P(f"RUN TIME landing {landing} -> T. Bird cut {tb} = {tb - landing} frames = {t:.3f} s = {int(t // 60)}:{t % 60:05.2f}")
    beat = int(lim) - 1                                  # one frame clear of the tie (knowledge/end_timing.md: 47102)
    P(f"record {RECORD_S} s = cut on {lim:.2f} for this landing -> beat = cut <= {beat}; "
      f"this route: {'UNDER' if t < RECORD_S else 'NOT under'} by {abs(RECORD_S - t):.2f} s; {beat - tb:+d} frames against {beat}; "
      f"{47040 - tb:+d} frames against the 47040 goal; cut == last input: {tb == len(ins)}")
    ok = same and tr_same and not lr and not ud and not unk and t < RECORD_S and tb <= 47102 and landing == 2074 \
        and not any("Start" in norm(b) for n, b in tail)
else:
    P("NO T. BIRD CUT in the trace: the route is not finished")
P(f"CHECK {'PASSED' if ok else 'FAILED'}")
(LOGS_DIR / "fix").mkdir(exist_ok=True)
(LOGS_DIR / "fix" / f"{route}_check.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
