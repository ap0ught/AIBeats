"""Second-pass patch 23 (stage 6 side job): port the integrator's wipe-out recovery for s6run.beam_search into the
LIVE file. Reported in knowledge/shared_requests.md (2026-10-12, integrator, chain1): from the real stage 6 state
(`$1A` 33) the boss beam died to the last line at depth 37 and solve() failed; fixed until now only in the
chain1 snapshot. The function is copied from chain1/contra/stages/s6run.py (their final version: back 8 depths at
the first wipe-out, then 17, width doubled up to 64, at most 5 recoveries); a fight that never wipes out is played
exactly as before. The live file's other functions (with this pass's progress_check / _in_trial) are kept."""
import shutil
from pathlib import Path

ROOT = Path(r"")
live = ROOT / "contra" / "stages" / "s6run.py"
snap = ROOT / "chain1" / "contra" / "stages" / "s6run.py"
A = "def beam_search(r, actions, score_fn, done_fn, key_fn=None"
B = "# ----------------------------------------------------------------------------- generic Spread fire policy"
s = live.read_text(encoding="utf-8-sig")
t = snap.read_text(encoding="utf-8-sig")
new = t[t.index(A):t.index(B)]
assert "keep_back" in new and "WIPE-OUT" in new
if "keep_back" in s:
    print("already ported")
else:
    bak = live.with_name(live.name + ".backup_before_wipeout_fix")
    if not bak.exists():
        shutil.copyfile(live, bak)
    new = new.replace("chain1 fix (2026-10-12):", "Wipe-out recovery (integrator's chain1 fix, 2026-10-12, ported to the live file):")
    out = s[:s.index(A)] + new + s[s.index(B):]
    tmp = live.with_name(live.name + ".tmp")
    tmp.write_text(out, encoding="utf-8")
    tmp.replace(live)
    print("ported:", len(s), "->", len(out))
