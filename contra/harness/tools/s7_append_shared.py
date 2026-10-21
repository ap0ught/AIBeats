"""Append the stage 7 second-pass lines to knowledge/shared_requests.md (append only; utf-8, temp + rename)."""
from pathlib import Path

p = Path(r"knowledge\shared_requests.md")
s = p.read_text(encoding="utf-8")
add = [
    "- 2026-10-12 (stage 7 second pass): a pause pressed on a stage's FIRST row is ignored by the game (stage 7: three "
    "\"phases\" made that way were all the same solve); on row 40, while Bill is still dropping in, it is taken. "
    "`ph80` + a 10-frame pause on row 40 reproduces `ph90` (same rows after subtracting 10, same `$1A` at every mark) "
    "to within one frame. Whoever shifts the global timer with a pause at a stage's start: not on row 0.",
    "- 2026-10-12 (stage 7 second pass): measured, relevant to every Spread fight: at most ONE bullet damages an enemy "
    "per frame and the other pellets stay alive inside its box (`code_enemies_bosses.md` A3 is right); with the "
    "10-bullet limit the damage at range is bounded by 10 pellets per flight time (about 0.3 HP/frame at 112 px, 1.0 "
    "from 35 px). Point-blank volleys into a thin box (rising wall, 16 px) do only 1 damage: the pellets spawn "
    "behind its centre; 25-45 px away they do 4-5.",
    "- 2026-10-12 (stage 7 second pass): `research.md` / `code_enemies_bosses.md` C2b call the stage 7 Barrier \"too far\" "
    "for the door; true, but it is what makes the stage fast: Bill is invincible through Heartbreak Alley (the record "
    "does this). The item cannot be collected from the floor (it bounces off the pillar at x 1584 back onto the pill "
    "box's ledge). Dropping through a ledge (Down+A) holds Bill's X for 17 frames.",
    "- 2026-10-12 (stage 7 second pass): `contra/stages/s6run.py` (runner shared by the stage 6 and stage 7 solvers) got "
    "two opt-in additions, `progress_check` and `_in_trial`; stage 6 does not set them (its boss search re-run gives "
    "the same 561 rows). The first pass's file is `s6run.py.backup_pass1`.",
]
if "stage 7 second pass" not in s:
    s = s.rstrip("\n") + "\n" + "\n".join(add) + "\n"
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(s, encoding="utf-8")
    tmp.replace(p)
    print("appended", len(add), "lines")
else:
    print("already there")
