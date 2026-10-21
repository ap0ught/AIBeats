# 013 — Armageddon: the Dark Queen (Level 13, level byte 13) — GAME BEATEN

## 2026-09-30

Arrival: `L13_load` (the toad dropping into the arena at x 28). The 1-player TAS's fight (FCEUX log
`tas/watch_1p_l13.txt`, 941 frames) is legal except its last few frames, but its inputs don't carry over: the
queen's moves depend on RNG and timers, and every alignment got our toad hit.

The hit counter: FCEUX RAM dumps every 10 frames of the TAS's fight show $586 climbing 0 → 240 in steps of 12.
The queen's own object (0x7E) shows hp 7 throughout. New `l4s.py` mode `ctr` (`L4S_CTR=586`, `L4S_CTRGOAL`):
rank = −counter·100 + 0.25·distance to the foe; goal = counter reached.
- `L13_f1`: 15 hits in 990 frames.
- `L13_f2`: to 240 (20 hits) in 240 frames. But 240 is not the end: idle, the queen keeps fighting.
- `L13_f3`: the 21st hit kills her (her object vanishes at frame 122 of the 124-frame section); the death
  animation, a countdown, then the cut to Professor T. Bird play out on their own.
Whole fight: 1,360 frames, finished at full health (hp 47; the byte blips 47→43→47 four times for 35 frames each — a flag bit, the hearts never drop; real damage costs 8).

**Verified from power-on: `python assemble.py fullrun_wip L1 L1to3 L3rat1 L3a L3mount L3t L4a L6a L8a L9a L10a
L11a L12a L13a` = 67,881 frames, replay MATCH sha1 13c76b69, 6 lives, full health.**
Speedrun clock (from the level-1 landing, frame 2,074): last hit at frame 66,560 = 17:53.000; the cut to
T. Bird (level byte 13 → 254) at frame 67,226 = **18:04.082**. World record 12:29.250.

Video: `video/fullrun_wip_overlay.mp4` (panel + burned-in captions), `video/fullrun_wip.srt`,
`video/fullrun_wip_script.md`; text from `video_text.py`, captions added to `render_overlay.py`.
