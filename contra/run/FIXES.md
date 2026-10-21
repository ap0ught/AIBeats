# chain2 - what had to be fixed, and notes for the solvers' owners

No solver file in the snapshot was changed. The only changed file is `contra/emulator.py` (the BizHawk path made
explicit so that the snapshot resolves to `chain2/`; original kept as `contra/emulator.py.snap0`), exactly as
chain1 did. Live solver files, frozen shared files, `chain1/`, `verify1/` and `yt/` were not touched.

## 1. Stage 3 climb failed from chain B's real state (owner: stage 3/8 builder) - solved by a solver parameter

* **What happened** (chain B, title_wait 1; stage 3's first frame 8,095, `$1A` 101, `$34` 189; log
  `logs/chain/B/s3_c2B_solve.out`): the climb reached row -70 normally (6 nodes) and then `row -73 seg 64-159:
  nothing valid of 22674 proposals`, the dead-end retry found nothing either, and `s3.solve` raised
  `RuntimeError: the climb did not reach the top floor`.
* **Why** (measured with `scratch/s3_probe.py` on the landing savestates the trials left in
  `states/s3_c2B/tmp/`): the jumps DID land on row -73 (Bill at X 124-125, Y 83), and Bill died 3-5 frames later
  in every case: a falling object (enemy type 11, slot 7) was coming down at X 109-110, Y 92-95 right where every
  proposal from the six row -70 nodes landed. `s3_climb.trial` rightly rejects a landing that dies within 8 frames.
  With `--keep 6 --tests 18` every kept row -70 node (all near X 119-126) led to the same landing spot and timing
  class; the wait rounds (up to 192 frames) and the firing modes (waits 0/8/24 only) did not get past it.
* **Fix:** none in the code. The stage was re-solved from the same real state with the solver's own options
  `--keep 10 --tests 36` (tag `c2Bb`, `python chain.py --chain B --tag c2Bb --extra 3 "--keep 10 --tests 36"`):
  row -73 then had 2 valid nodes and the stage finished (3,548 frames, verified from power-on).
* **For the owner:** when a row ends in "nothing valid", the climb could widen itself (more nodes kept at the rows
  below, firing modes with the long waits) before raising. Chain A's state (`$1A` 103) passed the same row with the
  defaults (3,490 frames).

## 2. Not fixes: what the chain found (nothing changed for these)

* **Stage 6, chain A: 4,204 frames (+154 against chain1) at the best phase of the table.** Start `$1A` 131
  (phase 3, predicted 4,029-4,038). Replayed and traced (`scratch/s6_lag.py`): rows 627-741 have 56 lag frames
  (every second frame), while Bill fires up-forward volleys into a screen with 4 soldiers (type 5) and 5 other
  objects (types 14/15) that the RNG put there; the tower cluster was then reached 56 rows later than in every
  table solve (tower1 at row 1,326 against 1,270), its jets were on another phase, and the cluster cost 895 frames
  (table: 791-837) with 9 deaths repaired. `s6_notes.md` already lists random soldiers as the stage's luck ("one
  of six starts lost about 50 frames"); the solver does not steer them and its fire policy does not avoid lag.
  For the owner: a lag-aware fire policy before the towers (fire only at a target that can be hit) and/or trying a
  short pause or wait to re-roll the soldier wave would protect the phase the chain pays for.
* **Press-history tails:** `tools/s2_solve.py` uses the last 40 history rows, `s6ctl` 12, `s3s8_lib` ~1,800,
  `s5` all; the chain hands every solver the whole real history and checks rule v2 with `check_inputs.py` on
  every prefix from power-on: every prefix of the delivered run passed.
* **Interfaces:** as in chain1 (`chain.py` ADAPTERS). New glue: stage 1 for any title wait (`tools/s1_open.py`
  + `contra.stages.s1` + opening/segment join, as `tools/s1_finish.py` does).
