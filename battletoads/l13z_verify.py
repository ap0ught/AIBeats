"""Power-on check of a route that ends with a T.-Bird-timed queen segment (l13solve2.py output):
    python l13z_verify.py <tag> <segment>...      e.g.  l13z_verify.py z1 L1b L3u L3skipu L4c5 L6c L8c L9c L10t L11r L12g L13z1
Builds the input list like assemble.py (same intro), replays it twice from power-on (once on the stock EmuHawk config,
once on the display-off config the search uses), compares the final RAM (SHA-1), counts banned presses, and reports the
frame of the landing (clock start) and of the cut to Professor T. Bird (second level-byte 13 -> 254) = the clock stop.
Writes logs/fix/<tag>.inputs.txt and logs/fix/verify_<tag>.txt. No A/V recording (assemble.py does that for the final)."""
import hashlib, json, sys
import toads.emulator as E
from toads.emulator import LOGS_DIR
import assemble

tag, segs = sys.argv[1], sys.argv[2:]
ins = []
for b, n, _ in assemble.INTRO:
    ins += [b] * n
bounds = []
for name in segs:
    j = json.loads((LOGS_DIR / f"pbeam_{name}.json").read_text())
    bounds.append((name, len(ins)))
    ins += j["inputs"]
(LOGS_DIR / "fix" / f"{tag}.inputs.txt").write_text(f"# frames={len(ins)} segments={' '.join(segs)}\n" + "\n".join(ins) + "\n")
banned = [i + 1 for i, b in enumerate(ins) if ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b)]


def replay(fast):
    if fast:
        import l13z_beam as zb
        e = zb.Emu(log_name=f"l13z_verify_{tag}_fast.log")
    else:
        e = E.BizHawk(log_name=f"l13z_verify_{tag}.log")
    t_start, cuts, prev_an, prev_lv = None, [], None, None
    lvl_first = {}
    for i, b in enumerate(ins):
        e.step(tuple(x for x in b.split("+") if x), 1)
        r = e.ram(0x10, 1)[0]
        if t_start is None and r == 1:
            an = e.ram(0x3B5, 1)[0]
            if prev_an == 5 and an == 4:
                t_start = i + 1
            prev_an = an
        if r != prev_lv:
            if prev_lv == 13 and r == 254:
                cuts.append(i + 1)
            lvl_first.setdefault(r, i + 1)
            prev_lv = r
    h = hashlib.sha1(e.ram_all()).hexdigest()
    lv = e.ram(0x10, 1)[0]
    e.close()
    return h, t_start, cuts, lv, lvl_first


out = open(LOGS_DIR / "fix" / f"verify_{tag}.txt", "a")
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.write(s + "\n"); out.flush()
P(f"== verify {tag}: {' '.join(segs)}")
P(f"{len(ins)} frames; segment starts {bounds}; banned presses (L+R / U+D): {len(banned)} {banned[:10]}")
h1, t1, c1, lv1, lf1 = replay(False)
P(f"replay 1 (stock config): sha1 {h1[:8]}, clock start (landing) {t1}, 13->254 cuts {c1}, final level byte {lv1}, level 13 from frame {lf1.get(13)}")
h2, t2, c2, lv2, lf2 = replay(True)
P(f"replay 2 (display-off config): sha1 {h2[:8]}, clock start {t2}, cuts {c2}, final level byte {lv2}")
ok = h1 == h2 and c1 == c2 and len(c1) == 2 and c1[1] == len(ins) and not banned
if len(c1) == 2 and t1:
    tb = c1[1]
    secs = (tb - t1) / 60.0988
    P(f"T. Bird cut at frame {tb}: time {(tb - t1)} frames = {int(secs // 60)}:{secs % 60:05.2f}  (record 12:29.25 = frame <= 47102; up14 was 47253)  "
      f"replay {'MATCH' if h1 == h2 else 'MISMATCH'}; {'VALID' if ok else 'NOT VALID'}; frames saved vs 47253: {47253 - tb}")
else:
    P("NO T. BIRD CUT FOUND", c1, "NOT VALID")
