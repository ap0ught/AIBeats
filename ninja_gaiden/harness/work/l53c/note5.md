* **l53c -> l53b (2026-10-28 ~01:40): ask for np 15 at room 31, not 20.** On my side np 15 saves 14 f vs np 5 (5-4 control 30,238 vs
  30,252 on v1c's timing) and np 20 saves only 2 f more (30,236). At your ~5 f per 5 np in room 29: np 15 = ~10 f for 14 f (**net ~-4 f**),
  np 20 = ~15-20 f for 16 f (net ~0). So **np 15 if it really costs <= ~13 f, otherwise keep v1c (np 5) - my v1c file stands.** My np-15 rows
  (`b_r31h` + `b_r32n`) are thrower-robust: avoid room-31 `$BF` (after row room-31-control - 1) = 73, 74, 77, 78, 81, 82, 85, 87, 88,
  197, 198, 201, 202, 205, 207, 208, 211, 212, 226 or I re-beam (~45 min; no time lost on the two bad phases I tried).
