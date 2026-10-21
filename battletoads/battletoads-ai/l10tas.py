"""Rat Race by the 1-player TAS's own inputs (2026-10-05): tas/watch_1p_l10.txt rows 60987 (placement (88,158)) .. 62884, no Left+Right
or Up+Down in it. Replay from our L10c bookmark (L9c_end0, the toad set down) with the landing re-sync; report the divergence and
whether the level ends. -> logs/pbeam_L10t.json if the level byte leaves 9."""
import json, re, os
from toads.emulator import BizHawk, LOGS_DIR
KEYMAP = {"le": "Left", "ri": "Right", "up": "Up", "do": "Down", "A": "A", "B": "B", "se": "Select", "st": "Start"}
rows = {}; ins = {}
for l in open("tas/watch_1p_l10.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+).*?p1=(\S+)", l)
    if m:
        r = tuple(int(v) for v in m.groups()[:9]); rows[r[0]] = r
        p = m.group(10); ins[r[0]] = [] if p == "-" else [KEYMAP[k] for k in re.findall(r"le|ri|up|do|se|st|A|B", p)]
seg = json.load(open(LOGS_DIR / "pbeam_L10c.json"))
def st(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x565], m[0x3B5])
e = BizHawk(log_name="l10tas.log"); e.load(seg["bookmark"]); m = e.ram(0, 0x800); print("our entry:", st(m), "lvl", m[0x10], "hp", m[0x51A], flush=True)
T0 = int(os.environ.get("L10_T0", 60987)); W = int(os.environ.get("L10_WAIT", 0))
e.step((), W); out = [""] * W; sync = T0; drift = None; hurt = None; end = None
for t in range(T0 + 1, 62900):
    if t not in ins: break
    b = tuple(ins[t]); e.step(b, 1); out.append("+".join(b)); m = e.ram(0, 0x800); r = rows.get(t)
    if r and r[3] == 0 and rows[t - 1][3] != 0:
        for _ in range(3):
            if m[0x475] == 0: break
            e.step(b, 1); out.append("+".join(b)); m = e.ram(0, 0x800)
    s = st(m)
    if r and drift is None and abs(s[0] - r[1]) <= 2 and abs(s[1] - r[2]) <= 2: sync = t
    elif r and drift is None: drift = (t, s, r[1:4])
    if m[0x11] < 3 and hurt is None: hurt = (t, "life lost")
    if m[0x10] != 9: end = t; break
if end is None:                                                   # the TAS log stops at its last input: idle on until the level byte leaves 9
    for _ in range(900):
        e.step((), 1); out.append(""); m = e.ram(0, 0x800)
        if m[0x10] != 9: end = ("idle", len(out)); break
m = e.ram(0, 0x800)
print(f"wait {W}: sync to {sync} (+{sync - T0}); first drift {drift}; {hurt}; level end {end} after {len(out)} frames (ours {len(seg['inputs'])}); toad {st(m)} lvl {m[0x10]} lives {m[0x11]}", flush=True)
if end:
    for _ in range(400):
        m = e.ram(0, 0x800)
        if m[0x10] == 10 and m[0x51A] == 47: break
        e.step((), 1); out.append("")
    e.save("L10t_end0"); json.dump({"bookmark": seg["bookmark"], "inputs": out, "slack": 0, "note": seg.get("note", "")}, open(LOGS_DIR / "pbeam_L10t.json", "w"))
    print("saved pbeam_L10t.json", len(out), flush=True)
e.close()
