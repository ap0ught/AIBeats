
### Round 2 STATUS at the end of the time-box (2026-10-20 01:15)
* NO new verified stage. The verified chain is still round 1's: power-on -> 2-1 control (frame 3,429),
  `logs/a12_chain.inputs.txt` / `logs/a12_act1.inputs.txt` (1-1 2,417 = record +107, 1-2 838 = record -3).
  No 3-1 control state to publish.
* Best partial 2-1 (legal by check, NOT finished, not open-loop verified to the stage end):
  `states/tmp/a12r2_2-1_room5.inputs.txt` = 2,229 rows after `states/a12_chain_1-2_end` (history
  `logs/a12_chain.inputs.txt`), reaching 2-1 room 5 (the last room) on frame ~5,656 = about +209 behind the record
  at the same point (record ~5,447). Rooms 2 (TAS lazy follow: record pace) and the pillar (brute force) are good;
  the losses are room 3 cols 2-17 (~150 f, beam) and room 4 (the chimney).
* Next command (queued, never started: free RAM stayed < 2.5 GB from 20:48 to 01:14):
  `python -u ng/stages/a12r2_solve.py 2 a12_chain_1-2_end --history logs/a12_chain.inputs.txt --rec work/a12r2/rec/r21.json --hybrid --prefix states/tmp/a12r2_2-1_room5.inputs.txt --prefix-frames 2229 --width 8 --chunk 8 --explore 4000 --hours 1.5 --tag w10`
  (room 5 is a TAS-legal leftward run; the hybrid reference makes it a lazy TAS follow), then 2-2 with `--hybrid`
  from its end state, then 2-3 (boss beam, `--tasref`; needs J&S + >= 10 ninpo, the 2-1 partial has J&S/10-15).
* Can the record's splits be beaten here? 1-1: only if the roof crossing is within ~15 f of the TAS (record +19;
  our best attempts +34..+53). 2-1: the record is TAS +103 but its route through room 3/4 is already the
  human-optimal legal one; our beam is ~+200 behind it, so the remaining work is room 3 (cols 2-17, plain
  running/jumping where TAS rows could be followed lazily if the beam resynced to the TAS line after the pillar)
  and room 4 (enter rising: jump at room 3's exit, wall-jump right from the left wall at (122, 209) with A+Right).
* Lessons: (1) where the TAS line is legal, the TAS reference + lazy follow is far better than the record
  reference (exact positions, ~1 emulation per chunk); use the record only around L+R / wall tricks (`--hybrid`).
  (2) Short hard spots (pillar, post, chimney) are solved faster by a small brute force over press timings
  (`work/a12r2/r3_brute.py`, `jump_brute.py`, `press_search.py`) than by the beam's explore. (3) Do not trust the
  beam's printed lag after an explore; measure first-reach times.
