
## Round 2 (agent a12r2, 2026-10-19 16:05 -> ; coordinator: beat the record's split per stage, use the record's route
## where the TAS line is banned)

### Record route extractor (done) -> `knowledge/record_route_a12.md`
* Frames cut with `states/tmp/a12r2_vid/extract.sh`, traced with `work/a12r2/rtrace.py` (agent a56's tracker reused,
  HUD mask 60) -> `work/a12r2/rec/r11/r12/r21/r22/r23.json`.
* `ng/legal.py` NEW (API addition, nothing changed): `Waypoints(rec_json, stage)` (calibrated RAM-coordinate route,
  facing-corrected x, camera rule for Ryu off-screen, `.time_map()` DTW to the TAS), `waypoint_ref(wp, f0)` (a
  StageBeam reference in record time). Driver `ng/stages/a12r2_solve.py` (a56's StageBeam, read-only import;
  `--rec` = record ref, `--tasref` = TAS ref; `--prefix`; legal 7-frame wall-climb macros), go-explore
  `ng/stages/a12r2_goex.py`, probes `work/a12r2/*_probe.py`, job queue `work/a12r2/runq.py` (RAM >= 2.5 GB).
* Per-column tables: `work/a12r2/rec/cmp_r11.txt, cmp_r21.txt, cmp_r22.txt` (`work/a12r2/cmp.py`).

### Findings
* 1-1: the record is TAS +0..4 to X 704, loses ~19 f at X 640-704 (roof hop instead of the pole double jump-off),
  then runs level with the TAS (+19) to the exit. To beat its split a legal 1-1 needs the roof crossing within
  ~15 f of the TAS. Attempts: record-ref beam (w1) +34 after the roof, then lost more on the flat part (+148 at
  f 1830; killed); go-explore g2-g5 (value = lag vs the record) all stall at X ~740 y 112 on the shop's top slab
  (a club enemy on the slab, `shots/a12r2_roof_1.png`; the record slashes it, t ~480). Not solved; round 1's
  1-1 v5 (2,417) stays in the chain.
* 2-1 room 2: the legalized TAS rows replay in sync even 127 frames late (StageBeam lazy follow with the TAS
  reference: whole room 2 at TAS pace, `--tasref`). Record-ref beam there lost ~40 f: use the TAS reference where
  the TAS line is legal.
* 2-1 room 3 start (pillar): TAS and record take the same line: climb the hazard pillar's left face, wall-jump
  left onto the small ledge (x ~110, y 160), jump right onto the pillar top (x ~170, y 128). The TAS's last jump
  is L+R (moving right while facing left); legal = land, hold Right 2-3 frames (turn), then Right+A.
  The 5-frame climb cycles (A+away x2, back x3) do NOT re-grab this wall; 7-frame (A+away x2, back x5) is the
  fastest that does (~1.1 px/f; TAS 2 px/f). Brute force (`work/a12r2/r3_brute.py`): pillar top on frame 4596
  (chain numbering; record pace + ~17, TAS +79). `states/tmp/a12r2_r3_best.inputs.txt` (1,167 rows after
  a12_chain_1-2_end, legal).
* 2-1 room 3 X ~363: the TAS jumps over a thin post to the big hazard block (X 391, y 128); a beam that
  falls short clings to the post (y 145) and stalls (t5 run lost 140 f there, `shots/a12r2_t5_3.png`,
  `shots/a12r2_tas21b_0.png`).
* 2-2 room 6: TAS rows followable (lazy) to the room exit; the exit uses L+R in the air (TAS 6709-6712): the
  record simply drops at x ~82-84. Room 7 start: the TAS goes left with L+R; the record goes right/up first
  (cols 13-15) - a TAS-ref beam stalls at X 834 y 82.
