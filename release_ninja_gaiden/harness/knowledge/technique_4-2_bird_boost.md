# Technique: the 4-2 exit-wall bird boost, without Left+Right (agent "wall", 2026-10-25)

**Status: the boost is LEGAL - found on the TAS's arrival state (TAS `$BF`): judge PASS, NesHawk = Mesen frame for
frame, trigger TAS +2 (no-boost legal TAS +14, record ~+26). On our locked chain (agent a's best lines, 2026-10-25) it
is NOT reachable at a gain: the bird's swing phase is wrong there (details in "On our chain").** Our 4-2 candidate
`l42_w_k932b` uses the no-boost wall (trigger 19,017 = TAS +21, 4-3 control 19,297 = record -4.8).

## What it is

The end of 4-2 is a climb up a LADDER column (collision kind 9) at world X ~3,040, from the floor (y 192) to the exit
tile above y 80. The stage ends (`$5C` 2 -> 0, then a fixed 279 f to 4-3 control) when Ryu is at X 3,035 with y <= ~84.
The homing bird (enemy type 11) that follows Ryu through the last part of the stage catches him **from behind while
he is in the air near the wall**. The hit costs 3 HP, and its knockback throws Ryu **toward the wall and up**:
+1 px/f in x (away from the bird), y -3 px/f for 5 frames then -2 px/f. Ryu reaches the ladder ~25 px higher than
a plain jump can, so the climb is ~12 frames shorter.

The TAS does exactly this. Its only banned inputs at the wall (A on consecutive frames, a 1-frame Right, Left+Right
on 18,679) come AFTER Ryu has touched the wall, in its climb. **The boost itself is Right held + one A+Right jump.**

## Exact inputs (demo from a fixed state)

Start: TAS 4-2 line at TAS frame 18,596 (NesHawk `states/l42w_tas18596.State` = `ref4751/09_4-2_control` + TAS rows;
Mesen `states/mesen/l42w_tas18596.mst`). Ryu is in a jump at X 2,933, y 176, hp 16, ninpo 10, J&S.

`work/l42w/wb_t596d.inputs.txt` (86 rows, frames 18,597-18,682):

| frames | input | what happens |
|---|---|---|
| 18,597-98 | A+Right | (A held from the jump; no effect in the air) |
| 18,599-630 | Right | land on the short post (y 176, X ~2,977-2,999) at 18,631 |
| 18,631-32 | A+Right | jump off the post at once (apex y 128 at 18,650, X 3,013) |
| 18,633-667 | Right | the bird comes up from behind-below; **hit 18,658** (Ryu X 3,025 y 131, bird x 199 y 138 vs Ryu x 208): hp 16 -> 13, 60 f of invincibility; knockback 18,659-668 carries Ryu to X 3,035 y 106 |
| 18,668-69 | A+Left | wall jump on the first frame Ryu touches the wall (still in the knockback pose) |
| 18,670 | - | |
| 18,671-73 | Right | back to the wall |
| 18,674-75 | A+Left | second wall jump (y 95) |
| 18,676-82 | Right | drift into the wall: **trigger on 18,682** (y 82) |

Judge (`check_inputs --period 5 --hold 2 --release 2 --windows 600:109,1800:246`): PASS. NesHawk replay from the
NesHawk state (`python -u work/l42w/nhwall.py l42w_tas18596 states/mesen/l42w_tas18596.mst work/l42w/wb_t596d.inputs.txt`):
same trigger 18,682, no divergence, no misread.

## Before / after (same start state, replayable files)

| line | file | trigger | vs TAS (18,680) | hp |
|---|---|---|---|---|
| TAS (illegal climb after the boost) | TAS rows | 18,680 | 0 | 13 |
| **legal bird boost** | `work/l42w/wb_t596d.inputs.txt` | **18,682** | **+2** | 13 |
| legal boost, plain ladder cycle after the contact | `work/l42w/we_t596_h13.inputs.txt` | 18,683 | +3 | 13 |
| no boost: post jump, ladder at the apex, 1.8 px/f ladder cycle | `work/l42w/we_t596_h16.inputs.txt` | 18,694 | +14 | 16 |
| the record's way (post, brick wall, ~4 wall jumps; video 20,630-20,723) | - | ~18,706 | ~+26 | - |

So the boost is worth **12 f vs our best no-boost climb and ~24 f vs the record's wall**, for 3 HP (HP carries into 4-3).

## Why it works (mechanics, measured)

* **Bird (type 11, slot 5 on the TAS line, spawned TAS 17,962 and homing ever since):** horizontal bang-bang homing
  (speed changes by 1/16 px/f per frame toward Ryu's x, so it overshoots and swings back), vertical 1 px/f toward Ryu's
  y. At the wall it closes from behind (left) at ~3.5-4 px/f, faster than Ryu's 1.5, so it catches him; it leaves at
  the right screen edge.
* **Knockback direction = away from the bird.** From behind it pushes Ryu into the wall; from the front it pushes him
  away from the wall (a loss). A hit while clinging to the wall gives no knockback (4-1 room-15 finding).
* **Knockback:** pose `$80` = 11 for ~10 f, x +1 px/f, y -3 (5 f) then -2 px/f; inputs are ignored until it ends or
  Ryu touches the wall; then a wall jump (A+Left) works on the contact frame. Invincibility `$95` = 60 f.
* **Hit window (map, `work/l42w/wmap.py`, 522 bird positions poked at 18,620 on the TAS line, `work/l42w/map620.tsv`):**
  hits from behind with Ryu airborne at X 3,014-3,029 (around the post jump's apex) give triggers 18,681-18,693; the
  best (18,681 with the plain cycle) are hits at X 3,022-3,025, y 130-132. Hits before X ~3,010 knock Ryu off the line
  (contact low or none), hits from the front never boost.

## Setting it up (how a human / our chain gets it)

1. Reach the short post (y 176) and jump off it right away (the post is the only thing higher than the floor; from the
   floor the apex is 16 px lower).
2. The bird must be behind Ryu and below/level, ~10-25 px back, when Ryu passes X ~3,015-3,025 near the apex. Its phase
   is set by everything before: arriving earlier/later, or a short stop (release Right) before the post, shifts it.
3. Hold Right through the hit and the knockback; on the frame Ryu touches the wall press A+Left (2 f), then Right x3,
   A+Left x2, Right to the trigger.

## On our chain (locked r15_c, `$BF` 81 at 4-2 control; agent a's lines b2_k3 / b2_kb1)

Searched (Mesen; every line also NesHawk-checked where it became a candidate):

| start | what | size | result |
|---|---|---|---|
| `l42a_k18932` (X 2,950, b2_k3) | jump timings x post jumps (`wenum`) | 2,172 approaches, 21 contacts x 51 climbs | best 19,019 no hit; no boost (no bird alive) |
| `l42a_k18880` (X 2,872) | same, from the floor | 1,344 / 72 contacts | best 19,018, no boost |
| `l42a_k18932` | wait 2-42 f at 0-50 f, then jump off the post on any post frame (`wpause`) | 526 stops, 7,094 jumps, 602 contacts | best 19,019 (no wait); the trailing type 13 never boosts |
| climb from the k932 contact | bounded frame beam, 12 inputs, width 5,000 | - | 19,017 (now the candidate) |
| `l42w_k18700` (b2_k3 without its bird kill) | frame beams keeping the bird alive, hp 15 | width 100-200, 5-7 inputs | every line is hit at 18,738-41 (front) or 18,839-43 (from behind, at equal x -> knocked back) |
| `l42a_b18760` (bird alive, 54 px behind) | beams keeping the bird alive to X 2,950 / to the ladder, 0-1 hits | width 200 | the bird can be kept alive and hitless only by NOT taking the +10 X 2,784; at the post (18,958) it is ahead of / level with Ryu; every line kills it or is hit from the front |

Why it fails on our chain (geometry and timing, not inputs):
* The boost bird is the type 11 that spawns around X 1,600 and homes on Ryu's screen x for ~1,000 f with a bang-bang
  swing (+-1/16 px/f per frame, amplitude ~90 px, period ~250 f). In the scrolling part Ryu sits at screen x 127, so
  the swing phase is fixed by the bird's spawn time and the line's lateness, not by Ryu's moves.
* On the TAS line the swing brings the bird up from behind exactly while Ryu is at the post jump's apex at X ~3,025.
  On our lines (TAS +11..+36 there, other `$BF`) it passes Ryu at ~18,738 (front), ~18,840 (behind) and ~18,945
  (front again), so at the post it is ahead of Ryu: a hit then knocks Ryu AWAY from the wall.
* Re-phasing it means ~60-125 f of lateness, or changing its spawn time (enemy slots near X 1,600) - far more than the
  ~12 f the boost saves. Waiting at the post (up to 42 f) only brings the trailing type 13 (it stays ~45 px behind and
  jumps to y ~137 only), which never boosts.
* So: the boost is real and legal, but on the locked chain it would need a different bird phase from the X ~1,600
  spawn on. If a future 4-2 line keeps the bird alive and has it behind Ryu at the post, run
  `python -u work/l42w/wenum.py <mst> <frame> --hist <h> --j1 0:30 --h 100` and then `work/l42w/wbeam.py ... --bound`
  for the climb.
