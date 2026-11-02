# Ninja Gaiden (NES, US) harness - day 1

Goal of the project: an AI builds a run of Ninja Gaiden from power-on that beats the human record (TheRetroRunner
11:32.183, speedrun.com Any%) under the board's own rules (`knowledge/project_rules.md`, `rules_verbatim.md`), and
later a separate TAS-mode attempt. This folder is the emulator harness, ported from `..\Contra\` (nothing is
imported from there). Nothing here claims a time against the record.

    Ninja Gaiden (USA).nes  the ROM (file CRC32 11F953F6, SHA-1 CA513F84...; MMC1 SxROM, 8 x 16 KB PRG)
    bridge.lua              runs inside EmuHawk, talks to Python over TCP
    ng/                     emulator.py, inputs.py, mode.py, events.py, clock.py, stages.py
    assemble.py             segments -> one input list from power-on, two replays, RAM + trace SHA-1, RUN TIME
    check_inputs.py         the input rules (press caps, holds, windows, no L+R / U+D), --tas switch
    tools/                  one-purpose scripts (below)
    knowledge/              ram.json (bridge fields), ram_notes.md (RAM proofs), clock.md, + the research files
    states/ shots/ logs/    savestates (states/dbg = RAM-poked DEBUG states, states/ref4751 = TAS replay states)
    dl/ work/               the research agent's downloads and work (read only: disassembly, TAS movies, record video)

## Launching

BizHawk 2.11.1 at `..\BizHawk-2.11.1-win-x64\`, **NesHawk only** (the constructor refuses another core and checks the
loaded one by its memory domains). Each instance gets a private copy of the base `config.ini` in
`emu_tmp\<pid>_<id>\` with rewind off and **`OpposingDirPolicy` = 2 (Allow)** (see "Opposing directions" below);
window placement is the base config's; `harness\tools\hide_emus.py` (already running) hides the windows.

    from ng.emulator import BizHawk
    from ng.mode import TICKS
    with BizHawk(log_name="x.log") as e:
        e.reset()                                  # power-cycle: framecount 0, row k -> frame k (bk2 numbering)
        e.tick(TICKS)                              # per-frame code counters (mode, game lag); after reset!
        s = e.step("Right+B", 10)                  # -> State: s.frame, s.x, s.stage, s.gm, s.lagged, ...
        s = e.run(rows)                            # per-frame button tuples, 2000 frames per round trip
        s, sent, carry = e.run_comp(rows)          # re-presses presses the game did not see (DMC conflict), pad $2A
        n, s = e.until(0x6D, "eq", 3, 5000, "Right")   # hold until RAM[$6D] == 3 or 5000 frames
        states, rams = e.run_ram(rows)             # + the 2 KB RAM after every frame
        e.trace(True); e.run(rows); e.last_trace   # one State per frame
        e.save("name"); e.load("name"); sid = e.msave(); e.mload(sid)
        e.ram(0x86, 1); e.ram_all(); e.oam(); e.screenshot("name"); e.poke(a, v)   # poke = DEBUG only
        e.watch("w", 0x63); ...; e.watchget()      # research: PCs that write/read/execute an address

* **Frame numbering (the Contra lesson):** a fresh launch connects at framecount 1 (frame 1 already emulated with no
  input), so row k is frame **k+1**; after `e.reset()` row k is frame **k** (= .bk2 numbering). Proven identical:
  `tools/launch_vs_reset.py logs/tas4751.inputs.txt 5000` -> same RAM SHA-1, 0 of 4,999 traced frames differ.
  `assemble.py`, `tools/trace_run.py`, `tools/events.py` use reset() unless `--launch`.
* **reset() drops Lua memory callbacks** (measured). `BizHawk.reset()` re-registers the ticks; `watch`es must be
  set again by the caller.
* **Input format** (`ng/inputs.py`, same as Contra): `logs/<name>.inputs.txt`, `# frames=N ...` header, one line per
  frame, buttons joined by `+`, empty line = nothing. Controller 1 only. Mask = the game's own byte `$2A`
  (A $80, B $40, Select $20, Start $10, Up $08, Down $04, Left $02, Right $01).
* **State fields** come from `knowledge/ram.json` "fields" (+ `lag`, `lagged`, and the tick counters when set).
* **Speed:** NesHawk ran 100-150 frames/s here today with the ticks on (the machine was shared). A full-game replay
  (39,084 frames) takes 5-7 minutes. At most 4 emulators; check free RAM first.
* **Stopping stray emulators:** only by PID, after checking the command line contains `Ninja Gaiden\emu_tmp`.

## Opposing directions (important)

BizHawk's default `OpposingDirPolicy` 0 ("Priority") silently drops one of Up+Down / Left+Right sent through
`joypad.set` (measured: Up+Down+Left reached the game as Up+Left). Movies bypass that filter, so the TAS 4751M
replayed through the bridge desynced at frame 806. Every harness instance now uses 2 ("Allow"): the console gets
exactly the row. The legal-run ban on L+R / U+D is enforced by `check_inputs.py`, never silently by the emulator.
(The Contra harness has the same default; its input lists never contain those combinations in a legal run, but a
TAS-mode Contra replay would be filtered.)

## Commands

| Command | What it does |
|---|---|
| `python tools/smoke.py` | launch, core/ROM identity, step, screenshot, RAM/OAM, speed, reset |
| `python assemble.py <route> <segment>... [--tail N] [--serial] [--launch]` | build `logs/<route>.inputs.txt` (segments: `.inputs.txt`, `.seg.json`, `blank:<n>`), replay twice from power-on on two emulators, compare RAM SHA-1 and the per-frame trace SHA-1, print the stage table, deaths, cutscenes, game-lag frames, START/END and RUN TIME; `logs/<route>.report.json`. Exit 2 on a mismatch |
| `python check_inputs.py <inputs> [--period 5 --hold 2 --release 2 --windows 600:109,1800:246 --buttons ..] [--tas]` | the Contra rule engine: controller 1 only, no L+R / U+D, per-button press period/hold/release, sustained windows. `--tas`: only controller 1 is enforced, the rest is printed as "info". Exit 1 on FAIL |
| `python tools/events.py <inputs> [--launch] [--states <dir>] [--name n]` | play an input list -> events report (`logs/<n>.events.json`, `logs/<n>.trace.csv`); `--states` saves a state + screenshot at every stage control frame, boss arrival, boss HP display 0, room entry |
| `python tools/trace_report.py <name>` | the same report from an existing `logs/<name>.trace.csv` |
| `python tools/ramwatch.py <state> [--inputs f / --hold Right+B] [--frames n] [--fields ..] [--addrs ..] [--diff] [--shots k]` | RAM watcher: chosen bytes, mode word and (--diff) every changed byte per frame |
| `python tools/trace_run.py <inputs> <name> [--launch]` | per-frame CSV of all fields + ticks |
| `python tools/intro_skip.py` | fastest power-on -> 1-1 with Start presses, found frame by frame (`knowledge/intro_skip.json`) |
| `python tools/cutscene_skip.py [route]` | every cutscene of a route: natural length vs greedy earliest Start skips (`knowledge/cutscene_skip.json`) |
| `python tools/clock_evidence.py start` / `end [state]` | the clock proofs: RAM vs OAM vs screenshots (`knowledge/clock_evidence.json`, `shots/clock/`) |
| `python tools/ram_verify.py` | RAM-map experiments with PASS/FAIL (`knowledge/ram_verify.json`, `shots/verify/`) |
| `python tools/mk_dbg_states.py [base]` | DEBUG: every stage start by "death warp" RAM pokes -> `states/dbg/stage_<name>.State` (never part of a run) |
| `python -I tools/bk2_to_inputs.py <bk2 dir> <name>` | a BizHawk movie's Input Log (data only) -> `logs/<name>.inputs.txt` |
| `python tools/launch_vs_reset.py <inputs> [n]` | fresh launch vs reset() equivalence |
| `python tools/dis6502.py <bank> <addr> [n]` | 6502 disassembly of the ROM (bank 7 = fixed $C000) |
| `python tools/probe.py <snippet.py> [state]` | run a snippet against one emulator (`tools/snips/` has the day-1 probes) |
| `python tools/contact.py <out.png> <png>...` | contact sheet of screenshots |

## Game mechanics the harness relies on (details and proofs: `knowledge/ram_notes.md`)

* **Mode** has no RAM byte: `ng/mode.py` counts executions of fixed code addresses per frame (bridge `tick`; a
  banked address only counts when its ROM bytes are mapped). `gm` = play loop `$C088`, `dw` death wait, `bk` boss
  tally, `se` stage end, `nx` next-stage load, `cs`/`csskip` cinematic engine and its script end, `title`/`act1`/
  `csdone` the power-on flow.
* **Input** is read in the NMI every frame (twice; on a mismatch - NesHawk's DMC conflict - the game keeps the
  previous buttons: 59 such frames in the TAS replay). No latency: row k acts on frame k. `$2A` held, `$29` new.
* **Lag:** BizHawk lag frames (NMI off) only during loads (33 in the whole TAS replay, all at power-on and stage /
  cutscene loads). **Game lag: none** - the play loop ran on every play frame of the 39,084-frame TAS (gm never 0
  inside play, never 2). But the main loop skips the timer, enemies and spawns on frames when a background column
  is waiting (`$4C` bit 6). A press that starts on a frame the play loop does not run is lost (`$29` is rebuilt
  every NMI).
* **RNG:** `$BF` is the only random source; +1 per NMI, i.e. per frame except the NMI-off load frames (31 stalls in
  the TAS replay, all at loads). It does not depend on input; only on time since power-on.
* **Stage flow** (TAS replay): stage exit walk/fade 127 frames -> `$6D` changes (load) -> control exactly 151 frames
  later; room changes take 23 frames; boss tally + exit ~129 frames; cutscenes after 1-2, 2-3, 3-3, 4-1, 4-4,
  5-3, 5-4, 6-3, 6-4a, 6-4b are skipped by Start (the TAS skips each on its first possible frame).
* **Power-on:** Start on frames 7, 15, 20 (rows after reset; one-frame presses, found by `tools/intro_skip.py` and
  identical to the TAS) skips the opening, starts the game from the title script and skips the ACT I card; 1-1
  control on frame **174**. Human-legal version (each Start held 2 frames): `logs/intro_human.inputs.txt`.

## The clock (`ng/clock.py`, proofs in `knowledge/clock.md`)

* START: N = first frame with `$33 == $97` in stage 0 (= first play-loop frame of 1-1; `$63` 150 -> 149). Ryu is
  first in OAM and in the picture on **N + 1** (`shots/clock/start_*.png`). START seen = N + 1 (174 -> 175).
* END: P = first frame of the final tally in 6-5 with `$63 == 0` (`$1FD == $D5`). The HUD redraws one of six parts
  per frame (`$3E` 5..0); the timer digits are buffered on a frame with `$3E == 1` and drawn in the next picture,
  so END seen = 1 + first frame > P with `$3E == 1` (TAS: P = 39,525, TIMER-000 first drawn on 39,530;
  `shots/clock/end_timer_sheet.png`).
* RUN TIME = (END seen - START seen) / 60.0988.

## Cutscenes (`python tools/cutscene_skip.py tas4751` -> `knowledge/cutscene_skip.json`)

Every cutscene before the end is skipped by ONE Start press, taken on the first frame the script loop runs (4-5
frames after the cinematic starts); control then comes 154 frames after the press (load + 151). The TAS already
presses on that frame everywhere (the greedy search found the same frames). Natural lengths, to play (control):

| after | natural -> control | skipped -> control | saved (frames) |
|---|---|---|---|
| power-on (opening, title, ACT I card) | the opening loops forever | Start on 7, 15, 20 -> 174 | - |
| 1-2 (Barbarian; scenes + ACT II card) | 8,331 | 3,302 | 5,029 |
| 2-3, 3-3 | > 6,000 frames (search limit) | 9,828 / 14,569 | > 5,800 |
| 4-1 (4-1 has its own scene) | 18,001 | 16,682 | 1,319 |
| 4-4 | 27,507 | 22,125 | 5,382 |
| 5-3 | 31,267 | 29,260 | 2,007 |
| 5-4 | 32,411 | 30,063 | 2,348 |
| 6-3 | 42,371 | 37,278 | 5,093 |
| 6-4a | 40,692 | 38,087 | 2,605 |
| 6-4b | 42,193 | 38,933 | 3,260 |

The power-on presses can be one frame long (TAS) or held 2 frames for the human rule (`logs/intro_human.inputs.txt`,
`check_inputs.py` PASS; `assemble.py intro_human ...`: control on 174 either way). The ending scene ($0B) cannot be
skipped, but it comes after TIMER-000.

## Verified on day 1

* **The harness replays the published TAS 4751M (39,084 frames, US ROM, NesHawk) in sync** once opposing directions
  are allowed: every stage load and control frame matches the research agent's movie playback.
* **Determinism / assemble:** `python assemble.py tas4751_full logs/tas4751.inputs.txt --tail 500`: two independent
  NesHawk instances from power-on, RAM SHA-1 `4bef831541c7` both, trace SHA-1 `093ce6869dff` both: MATCH.
  START RAM 174 / seen 175, END RAM 39,525 / seen 39,530, **RUN TIME 10:54.838 = 39,355 frames** (the TAS under the
  board's rule; the record is 11:32.183). Report: `logs/tas4751_full.report.json`.
* Fresh launch == reset() (above). reset() drops Lua callbacks (handled).
* The RAM map: `knowledge/ram_notes.md` (11/11 experiments PASS, HUD cross-checks, the TAS trace), `knowledge/ram.json`.
* The clock: `knowledge/clock.md` (START: OAM + screenshots, Ryu first drawn on N+1; END: one screenshot per frame,
  TIMER-000 first drawn on 39,530 = P+5, explained by the `$3E` HUD phase).
* Intro: the fastest Start presses (7, 15, 20 -> control 174) found by brute force equal the TAS's.
* `run_comp()` on the TAS's 1-1 (from `ref4751/00_1-1_control`, 400 frames): it re-pressed U+D on 204 and 517, the
  two frames after the game kept the old buttons (DMC conflict) - the mechanism works with pad `$2A`.
* `check_inputs.py`: the TAS FAILS the human rules (1,221 L+R frames, 3,430 U+D frames, press caps) and PASSES
  `--tas`; `intro_human` PASSES.
* States: `states/ref4751/` (75: every stage's control frame up to 6-4a - for the boss stages 1-2, 2-3, 3-3, 4-4,
  5-4, 6-4a that IS the boss arrival, the boss room is the whole stage -, the HP-display-0 frame of those bosses,
  every room entry (`room46_6-4b`, `room47_6-5` are the last two boss rooms' entries), and `21_6-5_movie_end`); they come from the TAS (banned inputs in their history): research/debug starting points
  only. `states/dbg/stage_<name>.State` (22): RAM-poked "death warp" starts (lives 1, ninpo 0, timer 150) - DEBUG
  only. `states/intro_fastest_end` = 1-1 control from a clean power-on with Start presses only.

## NOT verified / not done

* No legal-input route or search yet; no scoring function, no beam search (Contra's `resync.py` Pool/play were not
  ported: the bridge/emulator API is the same, so `Contra/contra/resync.py` is the template).
* The END rule was proven on the TAS's 6-5 only (one HUD phase). The `$3E` mechanism predicts 2..7 frames after P
  for other runs; check it again on our own final run with `tools/clock_evidence.py end <state>`.
* The picture-vs-video offsets against the record's video (30 images/s capture) are the research agent's
  (`record_notes.md`); a claim still needs the record's own video timing and an independent re-derivation.
* Natural lengths of the 2-3 and 3-3 scenes exceed the search limit (6,000 frames); not measured exactly.
* A/V recording (`record=`) is carried over from Contra but not exercised. No .bk2 exporter / hands-off movie check
  (`verify_bk2.py`) and no second-emulator (Mesen) cross-check yet.
* Hidden stage select `pick_area` ($C0E9) exists in the ROM but nothing calls it; the debug states use the death
  warp instead.
