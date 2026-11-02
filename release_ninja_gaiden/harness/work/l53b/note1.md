* **l53b (rooms 28-33) EARLY HP VERDICT (2026-10-27): hp 3 OK for rooms 28-33 as far as the data goes; e5's +2 hp buys at most one
  3-damage boost and none is planned.** Damage per touch (ROM table `enemy_damage` $B560, bank00, indexed by type; `hurt_ryu` $E144):
  thrower (t2) 1, **axe (t18) 1**, batter (t3) 1, crouching soldier (t5) 1, running soldier (t7) 1, bat (t8) 1, dog (t9) 1, jetpack
  ninja (t12) 1, its shuriken (t21) 1, machine-gun shot (t17) 1, waiting/crouched ghoul (t16/t15) 2, **bird (t11) 3, stone man (t14) 3,
  its ring (t22) 3**. So at hp 3 the birds (rooms 29-31), stone men (31-32) and rings (32) kill; everything else costs 1 (ghouls 2). The
  TAS runs rooms 28-33 at hp 3 with one 1-hp hit (room-31 axe boost, not on the legal floor+ladder exit). A 1-hp boost (axe, soldier,
  bat, ninja) stays possible on e4 (hp 3 -> 2 -> 1). Real e4 arrival checked: our room-28 state (l53a's rows, Mesen
  `states/mesen/l53b_e4_27857.mst`) = the TAS's 27,035 for Ryu; with the TAS's own rows the room-28 thrower #1 axe hits at our 27,980
  (TAS-eq 27,158), as prep predicted (spawn `$BF` 8 on e4). Working on a legal room-28 line that avoids it.
