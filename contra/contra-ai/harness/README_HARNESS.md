# Contra (NES, US) harness - day 1

Goal of the project: an AI builds a tool-assisted run of Contra that beats the human record (9:48.183, Angrylanks,
speedrun.com Any% "No Turbo", 1 player) under the record's own rules. This folder is the emulator harness. Nothing here
claims a time against the record: that needs the record's own video timing and an independent check.

    Contra (USA).nes        the ROM (file CRC32 C50A8304, UxROM)
    bridge.lua              runs inside EmuHawk, talks to Python over TCP
    contra/                 Python package: emulator.py, inputs.py, clock.py, resync.py, ramscan.py
    assemble.py             segments -> one input list from power-on, two replays, SHA-1 match, RUN TIME
    check_inputs.py         press-rate cap, no opposite directions, controller 1 only
    tools/                  one-purpose scripts (evidence, fitting a TAS movie, RAM capture, debug states)
    knowledge/              ram.json, ram_notes.md, clock.md, reference_run.md (+ the other agents' files)
    states/ logs/ shots/    savestates, logs and input lists, screenshots
    dl/tas/                 downloaded TAS movies (data only), dl/nes-contra-us/ the disassembly (read only)

## Launching

Emulator: BizHawk 2.11.1 at `..\BizHawk-2.11.1-win-x64\`. `contra.emulator.BizHawk(...)` starts EmuHawk the way the
Battletoads harness does: a private copy of BizHawk's config per instance (rewind off), `--lua=bridge.lua`, the TCP
port in `--userdata`; `harness\tools\hide_emus.py` (already running) hides the windows. Closing: `e.close()` or
`with BizHawk(...) as e:`. Each instance removes its private config folder (`emu_tmp\<pid>_<id>`) when closed.

    from contra.emulator import BizHawk
    with BizHawk(log_name="x.log") as e:          # core: NesHawk (default) or core="quickerNES" / env CONTRA_CORE
        s = e.step("Right+B", 10)                  # hold for 10 frames -> State (s.frame, s.x, s.lroutine, ... , s.lag, s.lagged)
        s = e.run(rows)                            # a list of per-frame button tuples, 2000 frames per round trip
        s, sent, carry = e.run_comp(rows)          # same, re-pressing presses the game did not see (see below)
        e.trace(True); e.run(rows); e.last_trace   # one State per frame
        e.save("name"); e.load("name")             # states/name.State
        e.ram(0x30, 1); e.ram_all(); e.oam(); e.screenshot("name")      # shots/name.png

* **Frames.** `s.frame` is `emu.framecount()`. The bridge gets control after frame 1, so from power-on input row k is
  applied on frame k+1. Frame 1 always has no input.
* **Input format** (`contra/inputs.py`): `logs/<name>.inputs.txt`, a `# frames=N ...` header, then one line per frame,
  buttons joined by `+` (`Right+B`), empty line = nothing. Buttons: Up Down Left Right Select Start B A. Controller 1 only.
* **State fields** come from `knowledge/ram.json` ("fields"); `lag` = BizHawk's lag counter, `lagged` = was the last
  frame a lag frame.
* **Speed.** NesHawk runs about 210 frames/s here (frameskip and speed mode do not help), quickerNES about 2,500.
  At most 4 emulators at once on this machine (shared).
* **Stopping stray emulators.** Only by PID, after checking the command line contains `Contra\emu_tmp`:
  `Get-CimInstance Win32_Process | ? { $_.Name -eq 'EmuHawk.exe' -and $_.CommandLine -like '*Contra\emu_tmp*' }`.

## Which core

**NesHawk is the harness's core.** Measured with identical inputs (`tools/core_cmp.py`): the random number `$34`
differs between NesHawk and quickerNES from the 12th frame (it is advanced by the idle loop, so it depends on exact CPU
timing), and NesHawk reproduces the console's DMC/controller-read conflict, which makes the game ignore the pad on some
frames (7 of 3,301 play frames in the stage-1 reference); quickerNES does not. A run built on quickerNES will not replay
on NesHawk. quickerNES is usable for throw-away exploration only.

**Lost presses.** On a frame the game ignores the pad, a one-frame press does not happen. `run_comp()` (bridge command
`stepc`) compares the game's own controller byte `$F1` with what was sent after every non-lag frame and presses a
missing button again on the next frame; it returns the rows really sent, which then replay open-loop. Any search
that uses one-frame presses must either use it or hold presses for 2+ frames (the project's press-rate cap needs 2+ anyway).

## Commands

| Command | What it does |
|---|---|
| `python tools/smoke.py NesHawk` | launch, identify the core, step, screenshot, RAM/OAM read, quit |
| `python assemble.py <route> <segment>...` | build `logs/<route>.inputs.txt` from segments (`.inputs.txt`, `.seg.json`, `pbeam_*.json`, `blank:<n>`), replay twice from power-on on two emulators, compare RAM SHA-1 and the per-frame trace SHA-1, print START/END, RUN TIME (frames / 60.0988), per-stage frames and lag, deaths, ignored-controller frames; writes `logs/<route>.report.json`. Exit code 2 on a mismatch |
| `python check_inputs.py <inputs> [--period 4 --hold 2 --release 2 --buttons B,A]` | the input rules: controller 1 only, never L+R or U+D, per-button press rate (cap is a parameter; default one new press per 4 frames, hold >= 2, release >= 2). Exit code 1 on FAIL |
| `python tools/clock_start_evidence.py` / `tools/clock_end_evidence.py <state> <seg>` | the clock proofs (RAM vs PPU OAM vs screenshots) |
| `python tools/ram_capture.py <inputs> <name>` then `tools/ram_verify.py <name>` | all RAM + OAM for every frame; the RAM-map checks |
| `python tools/ref_states.py <route>` | savestates at every stage's first frame / base room / boss kill of an assembled route |
| `python -I tools/unzip_tas.py`, `python -I tools/tas_convert.py <movie> <out>` | unpack / convert downloaded TAS movies as data (.fm2, .fmv) |
| `python tools/repair.py <state> <movie.inputs> <m> <out>` | fit one stage of a foreign TAS movie from a savestate (see knowledge/reference_run.md) |
| `python tools/build_ref.py <name> <movie> <S1,..,S8 or chain:M1>` | chain of stage fits from power-on |
| `python tools/mk_stage_state.py <stage> [weapon]` | DEBUG: a stage-start savestate made by writing RAM. Never part of a run |
| `python tools/first_effect.py`, `fit.py`, `watch.py`, `hp_trace.py`, `base_probe.py`, `pad_mismatch.py`, `core_cmp.py` | probes used on day 1 |

`contra/resync.py` has `Pool(n)` (n emulators on n threads, `pool.map(fn, jobs)`) and `play(emu, state, rows)` (load a
state, play, stop at death / fence stun / stall / level change) - the building blocks for a beam search
(`contra/*_toads_reference.py.txt` are the Battletoads beam searches, kept as reference text only; their scoring is
game-specific and was not ported).

## The clock

`contra/clock.py`, proven in `knowledge/clock.md`:

* START: N = first frame with `$2C == 4` (stage 1, not the demo). The medals are in the picture of frame **N + 1**.
* END: A = first frame with `$2C == 9` in stage 8; P = first frame after A with Bill standing, gun forward, on the
  ground (A + 1 if he is on the ground). The standing pose is in the picture of frame **P + 1**.
* RUN TIME = (END seen - START seen) / 60.0988 = (P - N) / 60.0988.

## Verified on day 1

* Determinism: `python assemble.py ref_stage1 logs/open_nh.inputs.txt logs/ref/s1.seg.json blank:242 blank:60` - 4,620
  input frames from power-on, two independent NesHawk instances: RAM SHA-1 `b6b87cc680a0...` both, per-frame trace SHA-1
  `41dd121319a5...` both. MATCH.
* The clock START on a run from power-on (RAM frame 591, seen 592) and the clock END with Up held and with Down held
  (RAM, PPU OAM and screenshots agree; see clock.md for the caveat about the stage-8 state).
* The RAM addresses in `knowledge/ram.json`.
* `check_inputs.py` FAILS the reference input list on press rate (B: 134 presses, 132 of them one frame long, 21 in the
  fastest second) and on 4 Up+Down frames - as it should; it passes controller-1-only and Left+Right.
* Savestates load across emulator instances; in-memory states (`msave`/`mload`) work.

## NOT verified / not done

* **No reference run through the whole game.** The current and previous 1-player TAS publications are Japanese-ROM
  movies; the only US-ROM 1-player movies are 2004 Famtasia files. None syncs. Fitted so far: stage 1 from power-on
  (real), and stages 5 and 8 (and whatever `logs/dbg/stage_report.json` lists) from debug stage-start states. The
  bases (stages 2 and 4) are not fitted. Details, numbers and what was changed: `knowledge/reference_run.md`.
* END was proven on a stage-8 state made with RAM pokes, not on a run from power-on.
* A/V recording (`record=`) is carried over from the Battletoads harness but was not exercised here.
* A second-core check (`core_check_toads.py` equivalent) was not ported: the two cores are known not to agree
  (above), so the open question is which other accurate emulator (Mesen?) should arbitrate, not whether quickerNES agrees.
* A .bk2 exporter / hands-off movie verification (`verify_bk2.py` equivalent) was not ported.
* The beam search was not ported; no scoring function exists yet.
