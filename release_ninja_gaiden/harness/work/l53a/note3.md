* **l53a (room 27) on e4 (5-3 control 27,360, hp 3 / np 45 / J&S): hp 3 OK for room 27 - 0 hits, NesHawk-verified.** Rows
  `work/l53a/ch1_rows.txt` (476 rows from the control row; row 1 = Left) -> **room 28 on 27,835 = stage row 476 = TAS +70**
  (record ~+110), **hp 3, np 45 -> 35** (2 spins: the y-112 platform walker + the TAS's 26,855 spin), J&S. NesHawk from
  `l52b_e4_27360` = Mesen on every frame to 27,865, end RAM equal; NesHawk states `l53a_27835` (room change), `l53a_27857`
  (room-28 control row - 1); Mesen `states/mesen/l53a_e4_27359.mst` (before the control row, 0 non-stack diffs vs NesHawk).
  Same rows on e1 (27,397, hp 6): identical path, room 28 on 27,872. **Verdict for 5-3: hp 3 OK / no hit is planned.** Room 27
  needs none; the TAS runs all of 5-3 at hp 3 (its only hit, 28,563 in room 31, is the axe boost the legal floor+ladder exit
  does not use); prep's legal exits end with no hits. What could cost hp: room-28 thrower phase (fix by an entry wait) and a
  ninpo shortfall (each missing spin ~ one hit). **Ninpo: np 45 covers the TAS's 11 spins + my 1 extra; spare only via the
  lanterns** (X 400: +5 for 2 f, Down+B plain slash; X 240 being priced). **Room-28 phase on e4:** x = (27,360 + 70) mod 256 = 38
  -> thrower #1 bad band (30-154) by 9: a 9-f faster room 27 or a re-scan with legal room-28 rows is needed (wait to 155 = 117 f: no).
