
## 5-2 lock round (room 23) (2026-10-27; agent l52a; tools `work/l52a/`)

On the locked chain `logs/l51_c3d_poweron.inputs.txt` (5-2 control row 24,998; our frame = TAS + 571 at the control).
Handover and states: `knowledge/LOCKED_CHAIN.md` "Agent notes (5-2)".

### Result
* **Room 24 on 25,496 = TAS +51** (TAS 24,874 + 571 = 25,445; record ~+72; old fallback r4_52_h2 +108), hp 12,
  np 50, J&S. Rows `work/l52a/c2_stage.txt` (power-on `logs/l52a_c2_poweron.inputs.txt`); NesHawk = Mesen every frame; judge PASS on the power-on file.
* Splits on this line: prefix (199 rows) = TAS exactly; the block climb (`b_r23a`) +12; the free +10 lantern (B 25,218-19, mid-air,
  np 40 -> 50, 0 f); walk off the y-96 platform instead of the TAS's jump to the wall; J&S pickup costs 2 blank rows in the air;
  floor + left shaft.
* Arrival for rooms 24-26: from the room change our frame = TAS + 622 (room-24 control row 25,519 = TAS 24,897); Ryu's state equals
  the TAS's (only np, `$BF`, timer, `$87/$89` and dead-slot junk differ; scripted rows give identical paths on both).

### Why the TAS's over-the-wall exit is not legal (bank 7 `touch_walls` $E677, `player_control` $EB7B, `ryu_body` $EFF1)
* `touch_walls` returns at once while Ryu's y < $48 (72): no wall flags, no facing update, no exit check above y 72.
  The touching byte `$8C`: bits 2/3 = wall on the left (`ground_flag` $0C of kind 1 at x-9), bits 0/1 = wall on the right
  (kind 2/3/5/6/8 at x+5), bit 5 = steps (kind 9 at x+5), bit 4 = floor, **bit 7 = "let go"**: set by a jump-off ($C0) or when a
  wall tile is overlapped from its passable side; while bit 7 is set and Ryu still overlaps any wall tile, NO wall bits are added,
  so he passes through. Kind 1 (the X-96 wall) blocks only from its right side; kind 2/9 (the X-48 column) only from its left.
* Facing: set LEFT by the wall-on-left flag at each check (y >= 72), right by $02/$20; a jump-off flips it (`eor #$40`) and sets
  run speed; in the air facing never changes otherwise. **In the air, holding the direction you face = run speed 1.5 px/f, holding
  away = drift 0.5 px/f** (`ctrl_left`/`ctrl_right`). U+D+L (pad $0E) maps to `ctrl_idle` (direction table $F087), which keeps
  the speed while `move_ryu` still steps left: that is the TAS's 1.5 px/f leftward flight while facing right. Legal Left (or
  Up+Left/Down+Left, $02/$0A/$06) always calls `ctrl_left` = drift when facing right; only frames with a NEW A or B press skip
  the speed write (they keep, never raise, it).
* The exit needs y in 72-84 with x-9 or x+5 inside the exit column (X 48-63), i.e. X <= 72 coming from the right. From the X-96
  wall's right face (clinging x ~120), that is ~48 px, so ~32 f at 1.5 px/f, while y must stay < 72 over X 105-120. Every legal way to
  be above y 72 there is a wall jump-off from that face, which always leaves Ryu FACING RIGHT (the check that frame set facing left,
  the jump-off flips it) -> 0.5 px/f -> ~96 f for 48 px; a jump-off rises 14 px and is ~30 px below its start 32 f later. A ground
  jump from the y-96 platform (left edge X 189) crosses y 72 coming down at X ~133 and y 84 at X ~131 (48 px rise, 1.5 px/f): 58 px short.
* The "grab inside the wall" case (Ryu back at y >= 72 at X 105-106, both checks inside the wall: flags $8C) turns him to face left
  and releases him next frame (bit 7), but with y speed 0 at y >= 72: he is at y >= 116 by X 72 (exact: Mesen test from TAS 24,848,
  Left / A+Right x2 / Left: X 90 at y 83).
* Only a knockback could break this: a hit from the right while Ryu clings at y 72-74 makes the next frame's grab happen at y < 72
  with stale wall flags and facing RIGHT, so the next A+Right jump-off flips him to face LEFT at run speed. Even that reaches
  X 72 only at y ~100 (jump-off at ~70, needs <= 54), and room 23 has no enemy that can reach the wall top (the waiting ghoul's long
  hop peaks at y 144; batters stay on the y-96 platform). So the record's line (left shaft) is the only legal exit.
* Search sizes behind this: prep's 3 beams from 24,820 (220 f) and `en23x.py` (4,638 legal cases), plus the code paths above.

### Other facts found
* **+10 lantern X 352: free** (any 2-3 f B in 25,217-25,223 on `b_r23a`, mid-air).
* **J&S lantern (X 144 y 112)**: sword breaks need Ryu y in 105-135 and the lantern 0-31 px in front (`slash_lantern` $DAA2); the
  power-up falls with gravity and is caught at |dx| < 12, |dy| < 17 (`take_powerup` $DB89). Walking off the y-96 platform, a slash
  breaks it but Ryu passes 1-2 px too low/early; 2 blank rows (25,351-52) + B 25,360-61 -> pickup 25,388 (cost 2 f; grid
  `jstest3.py`, 1,386 legal variants: no 0-blank catch, 1 blank breaks the Left-release rule).
  The Windmill (Up+B) never breaks it on this line (67 throw frames tested; on the platform a throw stops Ryu ~16 f).
* The waiting ghoul (type 16, `lurker_*` $CA2E) on the shaft floor X 77 wakes when Ryu is within 40 px and hops at him (long hop
  vy -4 when within 32 px). Running into it costs a hit from the left (pushed back right). c1 jumps over it at once from X 129.
* Left-shaft climb: contact-frame wall jumps on the left wall (X ~24) while facing right (drift back 0.5 px/f) climb ~12-13 px
  per 6-8 f; then a jump right onto the X-48 steps (kind 9, Up = 1 px/f) and a step jump-off into the exit tile at X 43 y 84.
* Block climb (25,180-25,240): the block's right face (X 376) and the X-400 column form a 19-px chimney; a hop gains 14 px, the
  floor jump peaks at y 144 and the block top needs y <= 128 at X 376, so two jump-offs are needed (`b_r23a`); a fresh beam
  (`b_blk1`, width 200) was not faster.
