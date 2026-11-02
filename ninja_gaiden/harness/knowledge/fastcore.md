# fastcore: Mesen 2.1.1 as a search core (NesHawk stays the judge)

Status 2026-10-22: **WORKS, in exact sync with NesHawk except NesHawk's DMC/controller conflicts**, which Mesen
cannot predict. Speed is only ~2x NesHawk per process. Use it as a fast, exact pre-filter / batch evaluator;
every result must still be replayed open loop on NesHawk (`verify_on_neshawk`) and pass `check_inputs.py`.

## Files

| file | what |
|---|---|
| `ng/fastcore.py` | Python API: `FastCore` (one headless Mesen process, batch runs, savestate slots), `MesenEmu` (BizHawk-like face), `convert()`, `verify_on_neshawk()`, `neshawk_pads()`; CLI `convert` / `speed` |
| `ng/fastcore.lua` | the Mesen side (test-runner script, TCP client) |
| `..\Mesen2\Mesen.exe` + `settings.json` | owner's official 2.1.1 build; `settings.json` (`{}`) = portable mode marker: settings, the extracted DLLs (`MesenCore.dll`, Skia/HarfBuzz), `Debugger\`, `Saves\` all stay in `G:\AI World Record\Mesen2\`. **Without it Mesen opens its first-run setup window.** The test runner never writes settings (`DisableSaveSettings`) |
| `work/fastcore/` | the evaluation scripts: `sync_test.py` + `replay_tpl.lua` (TAS replay + compare), `dmc_tpl.lua` / `dmc_run.py` / `dmc_an.py` (DMC timing study), `dmc2_tpl.lua`/`dmc3_tpl.lua` + `dmc_neshawk.py`/`dmc_n3.py`/`dmc_n4.py` (NesHawk DMC model attempts), `ildump.ps1` (IL dump of NesHawk), `fc_check.py` (API self-check), `legal_cmp.py`, `emu_check.py`, `pool_check.py`, `fc_validate.py` (search + NesHawk judge) |
| `logs/fastcore_pids.txt` | PID of every Mesen process fastcore started (kill only those) |
| `states/mesen/*.mst` (+ `.frame`) | Mesen savestates (Mesen-only format) with the NesHawk frame number |

## How Mesen is run (headless, no window)

    Mesen.exe --testrunner <rom> <script.lua> --debug.scriptWindow.allowIoOsAccess=true
              --debug.scriptWindow.allowNetworkAccess=true --debug.scriptWindow.scriptTimeout=1000000
              --nes.allowInvalidInput=true --timeout=<seconds>

* `--testrunner` (UI/Utilities/TestRunner.cs): `InitializeEmu(noAudio, noVideo, noInput)`, no Avalonia window,
  max speed, exits on `emu.stop(code)` or after `--timeout` seconds (default 100!). A Lua error does NOT stop it:
  the emulator keeps running until the timeout (fastcore sees the socket close / the script never connects).
* Started with `CREATE_NO_WINDOW`; checked with EnumWindows during runs: **no top-level window, visible or not**.
  `harness/tools/hide_emus.py` was therefore NOT changed. `FastCore` re-checks at start and logs a WARNING if a
  visible window of its PID ever appears.
* Any config value can be given as `--<section>.<property>=<value>` (ConfigManager.ProcessSwitch).
* Lua API used: `emu.setInput`, `emu.read/write(addr, [val,] emu.memType.nesInternalRam)`, `emu.addMemoryCallback`
  (exec/read; a read callback may return a value that replaces the read), `emu.addEventCallback` (inputPolled,
  endFrame), `emu.createSavestate/loadSavestate` (ONLY inside an exec callback of the main CPU), `emu.getState()`
  (flat map, e.g. `apu.dmc.timer.timer`, `cpu.cycleCount`), LuaSocket `socket.core` (needs allowNetworkAccess).
  The script watchdog (`ScriptTimeout`, default 1 s per callback) is raised because fastcore blocks in the NMI
  callback while it waits for Python.

## Sync test (TAS 4751M, US ROM, from power-on)

`python work/fastcore/sync_test.py logs/tas4751.inputs.txt logs/tas4751.trace.csv <tag> --ioff=1 [--force tracepad]`
compares 42 RAM fields (knowledge/ram.json) per frame with the NesHawk harness trace (`logs/tas4751.trace.csv`).

* **Frame numbering:** Mesen endFrame #f = NesHawk frame f (after `reset()`); the input of row f must be set at
  Mesen's input poll #(f-1) (scanline 241, just before the NMI that reads it) = `--ioff=1`.
* **Power-on RAM:** NesHawk fills RAM with `(addr & 4) ? $FF : $00`; Mesen's options are zeros/ones/random, so
  fastcore writes NesHawk's pattern in an exec callback on the reset vector `$FFDA` (first hit). Frames 1-6 then
  match field for field; the game clears what it uses anyway.
* **Opposing directions:** Mesen filters U+D / L+R unless `nes.allowInvalidInput=true` (same lesson as BizHawk's
  OpposingDirPolicy). The TAS needs them; legal runs never use them (check_inputs.py enforces it).
* **First divergence with plain inputs: frame 203** (`pad`/`padnew`/`anim`). NesHawk's game kept the previous
  buttons there (the DMC-DMA/controller-read conflict; 59 such frames in the TAS) and Mesen read the new buttons.
* **With the game's read forced to NesHawk's own pad byte** (fastcore writes `$28` and `$21` at `$F9D6`, the
  instruction after the second `read_joy`, so the game's two reads agree): **0 differing frames in all 39,084
  frames, all 42 fields** (stage/room/x/y/HP/timer/RNG `$BF`/boss HP/scroll/lag...). The legal chain
  `logs/a12r3_to22.inputs.txt` (power-on -> 2-2, 6,393 frames): 0 differences with NesHawk's pads, first
  difference at 3,533 (= NesHawk's first conflict there) with the plain rows. RNG, lag frames, the odd-frame /
  sprite / mapper timing all agree; the controller read is the ONLY difference.

### Why the conflicts differ (and cannot be predicted from Mesen)

The game reads `$4016` 2 x 8 times in its NMI (`$F9CC`/`$F9D3`, `read_joy` `$E819`) and keeps the old pad when the
two reads differ (`$F9D8 cmp $21`). A DMC sample DMA that halts the CPU on a `$4016` read clocks the shift
register once more (bit deletion). Both cores emulate this, but on different frames:
* Mesen (synced to NesHawk's game state): 386 frames with a DMA on a `$4016` read (17 reads logged); my DMC model
  from `emu.getState()` (timer, period, bitsRemaining) predicts every one of them to the cycle (385/386).
* NesHawk: 59 visible conflicts. **None** of them is a Mesen collision frame, and no constant cycle offset of
  Mesen's DMA schedule explains more than 20 of the 59 (`work/fastcore/dmc_an.py`; the best offsets repeat every
  432 cycles = 8 x the rate-15 period). NesHawk's DMC phase / halt timing differs from Mesen's in a way that is not
  a fixed shift (power-on DMC timer 1020 vs Mesen's, a different halt/re-read sequence, strobes only on odd APU
  cycles - see "NesHawk's DMC/joypad code" below); a first model of it does not predict the conflicts yet.
* Rate on legal play: 9 conflicts in 802 input changes (1.1 %) on the 6,393-frame legal chain, i.e. about one
  per 700 frames -> most stage-length solutions found on Mesen will meet ~1 NesHawk conflict.

**What a conflict does:** on frame k NesHawk's game uses row k-1's buttons instead of row k's (new presses on k
are lost for that frame). So NesHawk's outcome of rows R == Mesen's outcome of the "effective" rows R' with
R'[k] = R'[k-1] on every conflict frame k. Mesen reproduces NesHawk EXACTLY once the conflict frames are known
(proven on both long replays above and in the validation, step 3).

## Speed (this machine, shared with 5 EmuHawk instances, 2026-10-22)

* Headless Mesen with a Lua script: **~240-260 emulated frames/s per process** (the debugger is always on when a
  script runs and costs per CPU access and per PPU cycle; there is no switch to avoid it). With the 10 mode ticks
  and a record of every row: ~220 f/s. NesHawk through the bridge: ~100-120 f/s (trace_run: 117 f/s).
  -> ~2x per process, not 10x.
* Savestate: 6.3 KB; save 0.44 ms, load 0.50 ms per call including the TCP round trip (in-process slots).
* Batch: 50 candidates x 60 rows from one slot, every row recorded: 235 f/s including the 50 loads -> per-candidate
  overhead is negligible (NesHawk: one bridge round trip + mload per candidate).
* Power-on boot to 1-1 control (174 frames) incl. process start: 0.75 s. Boot to 2-2 (6,393 frames): ~27 s.
* `FastPool(2)` (two processes, threads): 40 x 300 rows = 12,000 frames in 25.7 s = **468 f/s aggregate** (~4x one
  NesHawk instance), identical results from both workers. The validation searches ran at 208-243 f/s per process
  including Python-side candidate generation and legality checks.

## API (ng/fastcore.py)

    from ng.fastcore import FastCore, MesenEmu, convert, verify_on_neshawk, neshawk_pads
    fc = FastCore(boot_rows=pads_or_rows[:N])     # power-on replay; idle at the checkpoint after row N (frame N)
    fc.save("s"); fc.load("s"); fc.get("s") -> bytes; fc.put("s", data); fc.drop("s"); fc.drop_prefix("k")
    fc.save_file("s", "states/mesen/x.mst", frame=N); fc.load_file("states/mesen/x.mst", "s")
    n, recs, status = fc.step(rows, record="all"|"last")         # from the current checkpoint; fc.frame advances
    res = fc.run_batch("s", [rows1, rows2, ...], record="all"|"last",
                       stops=[(0x6D, "changed", 0), (0x65, "==", 0)], record_ram=True, keep=True, prefix="k",
                       start_frame=N)
    # res[i].rows_played, .status (0 all rows / 1 stopped / 2 late checkpoint), .states (Row: fields by name,
    # the ng.mode tick counts gm/dw/bk/se/nx/cs/..., lagged, frame), .ram (2 KB), .slot (end state if keep)
    fc.ram(); fc.close()   (or `with FastCore(...) as fc:`)
    pool = FastPool(2, boot_rows=...); pool.save_all("s"); pool.run_batch("s", cands, ...)   # 2 processes
    apply_conflicts(rows, conflict_frames, first_frame)   # NesHawk's view of rows -> feed to fastcore

* Rows are ng.inputs button tuples or mask bytes. `masks_of(rows)`.
* A "checkpoint" = the CPU at the NMI entry `$F91A`; the state "after row k" is the checkpoint where row k+1 is
  read. All savestates are checkpoints. If the NMI is off right after a candidate's last row (load frames), the
  end checkpoint comes late: status 2 (its end state is not at row len). Avoid ending candidates in loads.
* `MesenEmu(boot_rows)`: `run/step/trace/last_trace/msave/mload/mfree/save/load/ram/ram_all/byte/state` like
  `ng.emulator.BizHawk` (State-like rows with the same field names + ticks + lagged). No `reset()` (Mesen's Lua has
  no power cycle: make a new MesenEmu), no `run_comp`, no screenshots, no watches.
* Converter: `python -m ng.fastcore convert <power-on inputs> <frame> <out.mst> [--pads <NesHawk trace csv>]` =
  replay rows 1..frame from power-on and save the Mesen state (+ `.frame`). Give NesHawk's pads (the `pad` column
  of a harness trace, `tools/trace_run.py`) when the history contains NesHawk conflicts; otherwise the rows are
  read cleanly and the state differs from NesHawk's after the first conflict. A NesHawk .State cannot be loaded
  by Mesen; reproduce it by replay (27 s for 6,400 frames).
* `verify_on_neshawk(history, new_rows, mesen_trace)`: NesHawk open loop from reset(), returns (first differing
  frame, NesHawk trace, NesHawk conflict frames inside new_rows).

## Recommended workflow

1. Get the start situation: `FastCore(boot_rows=neshawk_pads(trace, c0))` (or `convert` once and `load_file`).
2. Search with `run_batch` (many candidates per call, stops on room/stage change or death, keep end states).
3. Judge every result on NesHawk: `verify_on_neshawk` + `check_inputs.py` on the power-on list.
4. If NesHawk reports a conflict on frame k: Mesen with the effective rows (row k := row k-1) reproduces NesHawk
   exactly; either accept NesHawk's outcome (the rows are unchanged, so still legal) or re-search from frame k in
   Mesen with the effective history, and verify again. Expect ~1 iteration per ~700 frames.
5. Never put Mesen numbers in a report as a result: NesHawk's replay is the result.

Resource rules used here: <= 2 Mesen processes per agent, start only with free RAM >= 2.5 GB (FastCore checks),
1 while `logs/HOLD_FARMS` exists; kill only PIDs in `logs/fastcore_pids.txt`. Nothing runs from `Mesen2-master`.

## Validation (fastcore search -> NesHawk judge)

`python work/fastcore/fc_validate.py logs/a12r3_to22.inputs.txt logs/fc_to22.trace.csv <c0> <exit> <tag>`: a
small fastcore search ("delete one row" = do everything one frame earlier, screened by a 45-row look-ahead that
must land on the baseline's state one frame further on, then a full replay to the stage exit `$6D` change; legal by
`ng.solve.legality.check` on the whole power-on list), then: check_inputs.py on the power-on file, NesHawk open loop
from reset() with a per-frame compare (x, xsub, y, stage, room, hp, timer, rng, bosshp, pad, scroll, anim, ninpo,
lagged), and Mesen re-run with NesHawk's conflict frames applied. History = the legal chain `a12r3_to22`
(start state booted with NesHawk's own pad bytes, so it equals NesHawk's state exactly).

| stage | baseline exit | fastcore result (Mesen) | check_inputs | NesHawk open loop | Mesen + NesHawk's conflicts |
|---|---|---|---|---|---|
| 1-1 (c0 174) | 2,439 | **2,395 (-44 f**, one row deleted at frame 809; HP 11 instead of 12) | PASS | 1 conflict (frame 1192), so not frame-identical after it; **exit 2,395 = Mesen** | identical to NesHawk, every frame |
| 1-2 boss (c0 2,591) | 3,277 | 3,277 (no deletion found in 5 min) | PASS | **identical every frame, 0 conflicts**, exit 3,277 | - |
| 2-1 (c0 3,429) | 6,241 | 6,238 (-3 f, rows 4368-4370 deleted) | PASS | **desync**: 11 conflicts (3533 ... 5757), never reaches the exit within the rows | identical to NesHawk, every frame |

Files: `logs/fcv_<tag>.inputs.txt` (power-on rows through exit + 10, legal), `logs/fcv_<tag>.json`, `logs/fcv_<tag>.out`.
Reading: whenever NesHawk has no conflict inside the new rows the fastcore solution replays on NesHawk frame for
frame (1-2). When it has, NesHawk = Mesen-with-those-conflicts exactly, and the outcome may survive (1-1: same
exit frame) or not (2-1: the original rows reach the exit at 6,241 on both cores - NesHawk's 9 conflicts there
happen to be harmless - but doing frames 4368+ three frames earlier moved the inputs against NesHawk's
music-driven DMA schedule, 5 new conflicts appeared and one of them broke the run). The 1-1 result (-44 frames,
NesHawk-confirmed exit 2,395) is a real lead for the chain owners: `logs/fcv_s11.inputs.txt` rows 175-2405 (the
rest of the chain after the 1-1 exit must be rebuilt from there).

## NesHawk's DMC/joypad code (read from BizHawk.Emulation.Cores.dll 2.11.1 IL by reflection)

(`powershell -File work/fastcore/ildump.ps1 -TypeRegex <type regex> -MethodRegex <method regex>`: `System.Reflection` +
`MethodBody.GetILAsByteArray`, resolves tokens; no decompiler is installed.)
* DMC rate table NTSC (CPU cycles): 428,380,340,320,286,254,226,214,190,160,142,128,106,84,72,54. Power-on:
  `timer = 1020`, `timer_reload = 428`, `out_bits_remaining = 7`, buffer empty. `Run()` every CPU cycle:
  `timer--`; at 0 reload + `Clock()` (bits 7..0, at 0 take the buffer); buffer empty + length > 0 -> DMA
  `dmc_dma_countdown = 3`; a `$4015` enable with an empty buffer goes through `call_from_write` -> delay 3 (timer
  even) or 2.
* `NES.RunCpuOne`: while the countdown runs the CPU is halted (RDY) and `RunDMCHaltFetch` re-reads the CPU's
  address bus (a `$4016` there clocks the pad = bit deletion); the last count does the sample fetch.
  `read_joyport` ignores a second read of the same port on the very next cycle (`double_controller_read`).
  Joypad strobes are applied only on odd `dmc.timer` cycles (`APU.RunOneLast`).
* Ninja Gaiden writes `$4010 = $0F` (rate 15, 54 cycles) every time; samples are started by `$4015` writes
  (7,794 in the TAS). So DMA times are sound-driven (mostly the music: time since the stage started), hardly input-driven: deleting or adding a
  frame of input moves every later input relative to them (hence new conflicts after the 1-1 / 2-1 edits).
* Model test (`work/fastcore/dmc_neshawk.py`, `dmc_n3.py`, `dmc_n4.py`, Mesen logs `work/fastcore/out/dmc3.bin.dmc`):
  nearly every one of the 59 TAS conflict frames has a modelled NesHawk DMA within a few cycles of one of the 16 reads
  (or of a strobe), but so do ~10x more change frames without a conflict (the per-cycle alignment between the
  cores' CPU streams inside a frame differs by each core's own DMA stalls, and my stall correction made the fit
  worse). **No usable predictor yet.** A faithful port of NesHawk's per-cycle DMA path (RunCpuOne + MOS6502X RDY
  handling) into the Lua side would be needed; that is the open item if exact NesHawk replay without an extra
  NesHawk pass is ever required.
