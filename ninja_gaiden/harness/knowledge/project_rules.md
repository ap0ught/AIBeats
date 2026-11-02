# Ninja Gaiden project rules: DRAFT (research phase, 2026-10-19)

Goal: a tool-assisted run of Ninja Gaiden (NES, US) from power-on.
- It is a list of controller inputs replayed in BizHawk (NesHawk core).
- It must beat the human record by a wide margin under the board's own Any% rules.
- After that, a separate "TAS-mode" attempt with no human limits.
- The run is never submitted to speedrun.com (the board forbids movie files). It is measured against the record.

## The category and the yardstick

- speedrun.com Ninja Gaiden (NES) **Any%** (category `ndx8vvkq`). No sub-categories. The rules are in `rules_verbatim.md`.
- **ROM:** `Ninja Gaiden (USA).nes`.
  - SHA1 ca513f841d75efeb33bb8099fb02beeb39f6bb9c, file CRC32 11F953F6, headerless CRC32 7C4A72D8.
  - It is GoodNES "Ninja Gaiden (U) [!]", the same file as TASVideos' current movie.
  - The board accepts US and JP alike; we use US.
- **Record:** TheRetroRunner **11:32.183** (2023-08-05, NES console). Its own video, timed frame by frame, gives exactly 41,531 frames at 60 fps = **41,599 +/- 2 NES frames** (`record_notes.md`).
  - Next fastest: Arcus 11:33.933.
  - No faster time is claimed anywhere I found.
- **TAS reference:** TASVideos 4751M (eien86 & Scumtron), 10:50.33 TASVideos time. It is **10:54.78 under the board clock** (39,351 frames), but it uses inputs that are banned here (see below).
- **Working target:**
  - "wide margin" = at least 20 s under the record, so at most about **11:12**;
  - stretch goal, about 11:00 (8 s of L+R/U+D penalty on top of the TAS).
  - A legal-input TAS is estimated at about 11:03-11:10; to be refined.

## The clock (board wording, then RAM)

- Board: "Timing starts when you gain control of Ryu." "Timing ends when the timer reaches 000 after defeating the demon statue."
- What the moderators actually counted for the record: from the first video frame where **Ryu is visible** in 1-1 to the first video frame showing **TIMER-000**.
- **In RAM (proposed, from the TAS replay; the harness must confirm and write it down in a `clock.md`):**
  - START N = first frame with `$33 == 0x97` in stage `$6D == 0`. This is the autosplitter's start, and `$63` first reads 149 on this frame. The 4751M replay gives N = 174.
  - END P = first frame with `$6D == 21` (6-5), `$63 == 0`, after `$66` (boss display) reached 0. The 4751M replay gives P = 39,525.
  - Time = (P - N) / 60.0988.
- **Open picture offsets.** Measure them by screenshot in our emulator:
  - (a) how many frames after N Ryu is first drawn (TASVideos says about 2);
  - (b) how many frames after `$63 == 0` the HUD first shows 000 (the record video suggests the timer digits are redrawn at most every few frames).
  - Until measured, compare our runs to the record with RAM N to P, and claim nothing within 5 frames of a target.
- Nobody claims a record. A claim needs our run timed at the same two on-screen events, plus an independent re-derivation (owner's rule after Battletoads).

## Input rules (proposed; the coordinator decides)

1. **Controller 1 only.** Start from power-on, with no savestate in the final movie and no memory writes.
2. **Never Left+Right and never Up+Down on the same frame.**
   - L+R is a game rule; U+D comes from the linked general rules.
   - This kills the TAS's backward-speed preservation, its entry-ladder wall-clips and its U+D+L wall wobble.
3. **No turbo (APPROVED by the owner 2026-10-19: "keep the same rate as before, I think that was fair"). Each button:** a new press at most once every 5 frames (12 per second), every press held at least 2 frames and released at least 2 frames.
   - Sustained limits: at most 109 new presses in any 600 frames and at most 246 in any 1,800 frames (taken from the Contra record measurement).
   - Why: the record's video has no handcam and no usable click audio, so there is no Ninja Gaiden measurement (`record_mash_rate.md`).
   - Where the cap bites: slash-cancel mashing at Jaquio and the demon, the sword bosses, and A presses on rapid wall climbs.
4. **Down+B is two buttons.** Each counts against its own cap; never "one key mapped to two inputs" in spirit.
5. **Start** is allowed for skipping cutscenes, as the record and the TAS both do. A pause costs frames and shifts `$BF`.
6. **Deaths:** avoid them.
   - A death in Act VI sends Ryu back to 6-1.
   - Anywhere else, a death is only acceptable if it is measured to be faster, which is very unlikely; say so loudly.
7. **Glitches:** everything not banned is allowed: damage boosts, slash canceling, enemy-slot and subpixel manipulation, spawn delays, interrupt freezing, special-weapon persistence across rooms, pre-kills, any wall clip reachable without L+R or U+D.
8. **Core:** NesHawk for anything that counts. QuickNES only for throw-away search (NesHawk reproduces the DPCM controller-read conflict; the TAS had to be resynced for it).

## Per-stage yardstick (record vs TAS, seconds, from `record_notes.md` section 6)

The record's stage times (control to next control, the last stage to TIMER-000). The biggest gaps to the TAS are where a legal run must find its time:

| Stage | Record | TAS | Gap (NES f) |
|---|---|---|---|
| 2-1 | 48.33 | 46.62 | +103 |
| 2-2 | 51.60 | 48.17 | +206 |
| 3-3 boss | 15.17 | 13.78 | +83 |
| 4-1 | 36.47 | 35.16 | +79 |
| 4-3 | 42.55 | 39.83 | +163 |
| 5-1 | 40.93 | 38.32 | +157 |
| 5-2 | 40.90 | 36.29 | +277 |
| 5-3 | 49.67 | 44.11 | +334 |
| 6-2 | 52.47 | 48.64 | +230 |
| 6-3 | 48.47 | 45.19 | +197 |
| 6-4b Jaquio | 16.60 | 14.08 | +152 |
| 6-5 to 000 | 12.57 | 9.87 | +162 |
| all 22 stages | 692.18 | 654.76 | +2,248 |

Stage-builder comparison event: the first timer-running frame of each stage. `$62` begins decrementing; it is always 151 frames after `$6D` changes.

## Files

- `knowledge/`:
  - research.md, rules_verbatim.md
  - record_events.json, record_notes.md, record_mash_rate.md
  - tas_notes.md, game_mechanics.md, ram_map.md
  - this file
- `dl/`, all data and read-only:
  - `api/` speedrun.com JSON and the rules doc
  - `record_video/` the record VOD
  - `tas/` TASVideos movies and submission texts
  - `NinjaGaidenNES/` the disassembly
  - `NinjaGaiden-NES-autosplitter/`
- `work/`:
  - `vid/` record-video intermediates: downscaled frames, features, contact sheets
  - `tasrun/` the TAS replay: Lua, private config, per-frame RAM CSV, stage events
- `tools_research/build_record_events.py` rebuilds `record_events.json`.
