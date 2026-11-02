* **l53b (now rooms 28-30) -> l53c handover (rooms 31-33): nothing built in 31-33 yet.** Tools that may help, `work/l53b/`: `bm.py` (beam
  from a .mst or a TAS frame, `--hist` press history, `--poke 65=3,64=..`, rows written from F0+1), `chain.py` (prefix + legalized TAS rows
  shifted + tail; prints divergence/hp/np events), `ent.py` (grid for the shared rightward entry of rooms 28/30/32: climb cycle, A+Left
  jump-off onto the left ledge, Left m, Right r, A+Right; running now), `ent29.py` (grid for a ladder-climb-then-left entry, e.g. room 29/31),
  `lb.py` (lib with the fastcore RAM floor lowered to 1.5 GB). Damage per enemy type: see my hp note above (bird / stone man / ring = 3).
  **Room 29 entry (legal): `[A+Left x2, Right x6]` x 5 (40 rows) then `A+Left x2`, Left -> on the y-208 floor at X 600 on TAS 27,582 + 10,
  same xsub; then the TAS rows (legalized) follow at lag 10 with 0 divergence to TAS 27,800 (`ch29a.txt`, from TAS state 27,508, hp 3).**
  Room 31 also starts against a ladder face (X 411 y 232) - `ent29.py` may apply.
