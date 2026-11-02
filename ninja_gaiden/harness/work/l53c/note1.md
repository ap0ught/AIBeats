* **l53c (rooms 31-33 + 5-4) INTERIM 2026-10-27 ~19:35: rooms 31-33 and 5-4 built from TAS states, NesHawk = Mesen on every frame; waiting
  for l53b's room-31 arrival to graft.** Rows `work/l53c/c53_tas.txt` (1,556 rows from the room-31 control row = room-31 change + 24; chain
  script `work/l53c/c53.py <mst F0>` rebuilds them from any arrival). Splits vs TAS: **room 31 +54** (record +70; floor under the wall +
  a new 7-f wall-climb cycle `[A+Right x4, A+Left, Left, -]` = 1.86 px/f), **room 32 +7** (turn on the left ledge, no moonwalk), **room 33 +
  transition -1** (Right held; the stage end WAITS FOR START: Start on trigger + 5/6), **5-4 = TAS +0** (b13's kill, one Start on kill + 594
  -> 6-1 load on kill + 597; b13's own Starts cost it 2). **5-4 control row = 5-3 trigger + 160** (not + 159). Total from the room-31
  change to the 6-1 load: TAS + 60. **Needs at the room-31 control: np 20** (spins: room 31 x2 (TAS 28,508-eq + one for the bird/axe),
  room 32 x1 (TAS 28,782-eq); exit 5 for 5-4's one spin), J&S, any hp >= 2 (no hits taken; the transition refills to 16). **Room-31
  thrower: `$BF` after the row before the room-31 control row must NOT be 73, 74, 77, 78, 81, 82, 85, 87, 88, 197, 198, 201, 202, 205,
  207, 208, 211, 212 or 226** (TAS 234; 237 of 256 good). **5-4 tally:** `$62` at the 5-3 trigger <= 55 or it costs 3 f. Rooms 31-33
  rows do not depend on anything else found so far (room 32/33 and 5-4: `$BF`-free). Details: `work/l53c/sec_draft.md` (to be merged
  into legal_a56_notes.md "5-3 rooms 31-33 + 5-4").
