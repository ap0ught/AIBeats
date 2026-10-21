# chain2 - the best complete run with the current solvers (2026-10-16)

**`run_chain2.inputs.txt`: 34,567 input rows from power-on through all eight stages (chain C, title-screen wait 3).
START (medals, RAM) frame 593, END (Bill stands, RAM) frame 34,508: 33,915 frames = 9:24.321 at 60.0988 frames a
second, by `contra/clock.py`. No death, weapon `$13` at every stage start from stage 2 on, `check_inputs.py` at its
defaults (rule v2: 5-frame rule + at most 109 presses per 600 frames and 246 per 1,800) PASS.** Two fresh-launch
replays from power-on: RAM sha1 `2242cdd88af3...` both, per-frame trace sha1 `23c8ac98fd9f...` both: MATCH.
Made by running the eight current stage solvers in order, each from the real state the previous one left, from a
private snapshot of the project (`SNAPSHOT.md`). This states measured numbers only; it claims no record. An
independent verification follows.

## Result (chain C; segment = a stage's first `$2C == 4` frame to the next stage's, stage 8: to END P)

| stage | first frame | segment | record | ours - record | chain1 | ours - chain1 | lag | Start presses | B presses | ahead of the record at the stage's end |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 593 | 3,905 | 3,907 | -2 | 3,900 | +5 | 16 | 0 | 97 | +2 |
| 2 | 4,498 | 3,600 | 3,716 | -116 | 3,604 | -4 | 25 | 0 | 160 | +118 |
| 3 | 8,098 | 3,516 | 3,934 | -418 | 3,542 | -26 | 36 | 0 | 32 | +537 |
| 4 | 11,614 | 5,155 | 5,761 | -606 | 5,269 | -114 | 22 | 0 | 277 | +1,143 |
| 5 | 16,769 | 6,040 | 6,125 | -85 | 6,041 | -1 | 13 | 0 | 158 | +1,228 |
| 6 | 22,809 | 4,059 | 4,143 | -84 | 4,050 | +9 | 13 | 6 (3 pauses) | 115 | +1,312 |
| 7 | 26,868 | 4,413 | 4,488 | -75 | 4,831 | -418 | 17 | 6 (3 pauses) | 157 | +1,387 |
| 8 | 31,281 | 3,227 | 3,273 | -46 | 3,237 | -10 | 0 | 0 | 82 | +1,434 |
| **total** | END 34,508 (seen 34,509) | **33,915 = 9:24.321** | 35,349 | **-1,434** | 34,474 (9:33.622) | **-559** | 142 in play (159 from power-on) | 12 | 1,078 (+1 title Select, 1 title Start) | |

Record segments: `knowledge/project_rules.md` (video frames x 60.0988/60, +/- 2 each; their sum is 35,349). Pauses are
5 frames each (Start pressed at frames 24,223/24,228, 24,255/24,260, 24,767/24,772 in stage 6 and 28,078/28,083,
29,808/29,813, 29,872/29,877 in stage 7), chosen by the stage 6/7 solvers. Highest new-press counts in any 60 /
600 / 1,800 frames: B 12 / 70 / 144, Down 12 / 44 / 76, Right 8 / 50 / 129, Left 8 / 52 / 136, A 2 / 14 / 38,
Up 10 / 15 / 18, Start 4 / 6 / 6 (limits 109 per 600, 246 per 1,800). Controller-ignored frames (DMC read conflict,
assemble's count): 35. Full table: `table.md`; everything: `run_chain2.report.json`.

## The three chains and why these title waits

| chain | title_wait | `$1A` at stage 6 (phase) | stage 6 | stage 7 | total | proof |
|---|---|---|---|---|---|---|
| A | 0 (verified rule v2 stage 1 list, not re-solved) | 131 (3: best band 0-10) | 4,204 | 4,421 | 34,054 = 9:26.634 | ALL_OK (`runs/A/proof/`) |
| B | 1 (verified rule v2 stage 1 list) | 189 (61: worst band) | 4,060 | 4,452 | 34,007 = 9:25.852 | ALL_OK (`runs/B/proof/`) |
| **C** | **3** (stage 1 solved for this wait) | 152 (24) | 4,059 | 4,413 | **33,915 = 9:24.321** | **ALL_OK** (this folder) |

`$1A` advances by one on every non-lag frame (checked on every hand-over: `$1A(next) = $1A + segment - lag`), so
the stage 6 phase is the title wait's `$1A` plus everything before it. Chain A's stage 6 started at phase 3, in
the table's best band (predicted 4,029-4,038), and still took 4,204: a random soldier wave plus up-forward volleys
gave 56 lag frames at rows 627-741, the towers were reached 56 rows late on another jet phase, and 9 deaths had
to be repaired (FIXES.md, section 2). No other wait could give a better band than A's, so the two extra chains
kept the phase near the best band and changed the RNG: wait 1 (same `$1A`, other `$34`; predicted phase about 1)
and wait 3 (`$1A` + 2, predicted phase about 5). Scatter in stages 2-5 (stage 3 alone moved 3,490 / 3,548 / 3,516)
moved their real stage 6 phases to 61 and 24; both still beat A's stage 6 by about 145. B and C ran in parallel
(at most 6 emulators). Chain C is the fastest complete run and is the delivered one.

## What is verified, and how

* **Replays from power-on, fresh emulator instances (NesHawk):** every prefix once when its stage finished (next
  stage's first frame exactly on the last row, weapon `$13`, no death) - the next solver started from the state
  saved in that replay; the whole run four times (the chain's own end check, `assemble.py`'s two replays with
  matching RAM and trace sha1, and `clock_shots.py`).
* **Input rules:** `check_inputs.py` at its defaults (rule v2 windows) PASS on the full list and on every prefix
  of every chain.
* **No death** (assemble's count and the chain's own), weapon `$13` at every stage start from stage 2.
* **Clock:** `$2C` first 4 on frame N = 593; medals in the PPU sprite memory and the picture on 594
  (`shots/clock/start_f593.png` none, `start_f594.png` two medals). `$2C` first 9 on A = 34,507 with Down held;
  P = 34,508; the pose changes in the game's sprite buffer on P and in the PPU / picture on P + 1
  (`end_f34508.png` prone, `end_f34509.png` standing, looked at by eye). Time = (P - N) / 60.0988 = 33,915 frames.
* **Not verified / assumed:** the record's numbers (taken from the project's notes); that the leaderboard times
  the same two picture events; any other emulator or core (NesHawk only); an independent re-derivation (to follow).

## Files

| file | what |
|---|---|
| `run_chain2.inputs.txt` | the run (row i, 0-based, is applied on emulator frame i + 2 of a fresh launch; the last 60 rows after P are an untimed tail) |
| `run_chain2.report.json` | the proof: two-replay hashes, clock, per-stage table, presses, check_inputs, clock evidence summary, the chain's own records |
| `table.md`, `run_chain2.check_inputs.json`, `logs/run_chain2.report.json` (assemble), `clock_evidence.json`, `shots/clock/` | parts of the proof |
| `chain.py` | the chain (from chain1's: named chains `--chain`, any title wait `--wait`, rule v2 check on every prefix); resumable |
| `run_s67.py`, `finish.py`, `clock_shots.py` | stage 6/7 glue, the final proof, the clock screenshots (from chain1's) |
| `chain_A.json`, `chain_B.json`, `chain_C.json` | what each chain verified (per stage: frames, lag, `$1A`/`$34`/lives, solver info, check_inputs) |
| `runs/<X>/` | `through_sK.inputs.txt` (power-on to stage K+1's first frame), `run.inputs.txt`, the press history each solver got (`prior_sK_*`), finished solves; `runs/A/proof`, `runs/B/proof`: their finish reports |
| `states/<X>/sK_pre.State`, `sK_start.State` | the real states one frame before / on stage K's first frame, saved from the power-on replays |
| `logs/chain/<X>/` | chain logs and every solver's output |
| `SNAPSHOT.md`, `FIXES.md`, `snapshot_table.py`, `scratch/` | snapshot record (size, sha1), fixes and findings, diagnosis scripts |

## How to reproduce

From `` (Python 3.13, BizHawk 2.11.1 at `..\..\BizHawk-2.11.1-win-x64`):

    python finish.py --chain C            # the proof for chain C's run (copies it to run_chain2.inputs.txt): about 10 min
    python assemble.py run_chain2 run_chain2.inputs.txt
    python check_inputs.py run_chain2.inputs.txt
    python chain.py --chain C --table
    python chain.py --chain D --wait 5    # a new chain (about 2.5 h; stages 1, 3, 5, 8 use 3 emulators)

Wall time: chain A 2 h 2 min, B 2 h 20 min (including the failed stage 3 attempt), C 2 h 33 min (stage 1 solved); solver
time per stage in `table.md`. The solvers search with real emulator timing in places, so a re-run is not
guaranteed to give the same rows; every result is checked by the same replays.
