# Ninja Gaiden (NES, US): research for an AI run under the speedrun.com Any% rules

Status: first pass complete, 2026-10-19. The owner approved using any information found online.

Labels used across these files:
- **[stated: X]** = said by source X.
- **[measured]** = my measurement on downloaded data.
- **[replay]** = seen in BizHawk 2.11.1 (NesHawk) replaying TASVideos 4751M with a RAM-logging Lua.
- **[inference]** = my reasoning; verify it.

Companion files:
- `rules_verbatim.md`: all board rules, verbatim.
- `record_notes.md` + `record_events.json`: the record timed on its own video, with splits and the TAS comparison.
- `record_mash_rate.md`: why there is no press data; the proposed cap.
- `tas_notes.md`: TASVideos movies, sync check, board-timed TAS, banned-input counts.
- `game_mechanics.md`: structure, timer, movement, weapons, manipulation, route landmarks.
- `ram_map.md`: compiled RAM map, unverified except where marked.
- `project_rules.md`: draft rules for our run.

---

## 1. ROM

- Ours: `G:\AI World Record\Ninja Gaiden\Ninja Gaiden (USA).nes`, 262,160 bytes.
  - SHA1 `ca513f841d75efeb33bb8099fb02beeb39f6bb9c`.
  - File CRC32 `11F953F6`; without the header: CRC32 `7C4A72D8`, MD5 `07c1b92ae9b78f209075a8cc6d3eebf0`.
  - iNES header `4E45531A 08 10 10 00...`: mapper 1 (MMC1, SLROM), 8 x 16 KiB PRG, 16 x 8 KiB CHR. [measured]
- It is **GoodNES "Ninja Gaiden (U) [!]"**:
  - the SHA1 equals TASVideos' version 1066 and the 4751M bk2 header;
  - the headerless MD5 equals the 3223M fm2 checksum;
  - the disassembly's `NinjaGaiden.sha1` is the same.
- The Japanese version is "Ninja Ryuuken Den" (TASVideos version 6363, SHA1 fcd14af7...). The 2026 damageless TAS uses it, and its judge notes the game "also plays fine in the US version".
- **The board has no ROM-version rule.** US and JP runs share one board (#8 beco and #13 ohon are JPN). The PAL version exists as a region option. We use US.

## 2. Board, category, record

Source: the speedrun.com API (`dl/api/`).
- `https://www.speedrun.com/api/v1/games/ngnes?embed=categories,levels,variables,platforms,regions` (follow the redirect; the game id is `lde39l63`)
- `https://www.speedrun.com/api/v2/GetGameData?gameId=lde39l63` (game rules text)
- `.../api/v1/leaderboards/lde39l63/category/ndx8vvkq?top=25&embed=players,platforms,regions`
- `.../api/v1/runs/z5pwrgdm?embed=players,platform,category`
- `.../api/v2/GetGuideList?gameId=lde39l63` and `GetResourceList?gameId=lde39l63`

Board rules in short (verbatim in `rules_verbatim.md`):
- **Clock:** "Timing starts when you gain control of Ryu." "Timing ends when the timer reaches 000 after defeating the demon statue." Realtime only. No milliseconds at 11:50 and above.
- **Banned:** "Left+Right is not allowed." "Turbo is not allowed." The linked Google doc adds "Left+Right or Up+Down is not allowed", plus no save states, RAM watch, rewind, movie files, remapping, or multiple inputs on one key.
- **Emulators:** Mesen (no run-ahead), MesenRTA (preferred), BizHawk/NesHawk, puNES, Nestopia, FCEUX; OpenEmu for Mac. Banned: Gotvg, RetroArch, Jnes.
- **Other:** the reset or power-on must be in the video; the emulator version must be named.
- **No banned glitches.**
- **Categories:** Any% (ours), Low%, Pacifist, Damageless, 100%, 2P1C (archived). **No variables, so no sub-categories.**

### Any% leaderboard, top 10 (API, 2026-10-19)

| # | Runner | Time | Date | Platform / notes |
|---|---|---|---|---|
| 1 | **TheRetroRunner** | **11:32.183** | 2023-08-05 | NES console, USA. https://www.twitch.tv/videos/1890225973 |
| 2 | Arcus | 11:33.933 | 2025-11-13 | NES, PowerPak (mod-retimed). https://www.twitch.tv/videos/2617831358 |
| 3 | Lainerainer | 11:37.650 | 2026-08-09 | NES. https://youtu.be/zLITWse7nGQ |
| 4 | blacksquall | 11:37.667 | 2026-02-18 | Mesen 0.0.7 (MesenRTA). https://www.youtube.com/watch?v=rM8Tk-oBmVQ (raw: UIle0bzSoyQ) |
| 5 | PensiveMoose | 11:39.600 | 2022-12-16 | NES, USA. https://youtu.be/8hTp82jdhkw |
| 6 | knuckle_buster | 11:39.817 | 2025-11-05 | NES + Everdrive. https://youtu.be/Vre52snGXwY |
| 7 | GetThis | 11:42.533 | 2025-11-01 | NES. https://www.twitch.tv/videos/2607251609 |
| 8 | beco | 11:44.237 | 2020-02-23 | NES, **JPN**. https://www.twitch.tv/videos/556116240 |
| 9 | beerfullofbelly | 11:44.733 | 2026-01-31 | NES + Everdrive N8 Pro. https://www.youtube.com/watch?v=mBvNukEQopA |
| 10 | MisterAves | 11:45.733 | 2023-10-01 | EmuHawk 2.6.1 (mod-retimed). https://www.youtube.com/watch?v=5LU1KETtuyE |

- The full top 25 is in `dl/api/lb.json`.
- **Faster times referenced off the board:** none found. The TAS 7532S notes mention Arcus's and TheRetroRunner's 2022 PBs (11:35 and 11:34), which are slower.
- The record holder's own estimate of the run's potential is "maybe a low 31 or high 30" without the missed 5-1 manip.
- Guinness lists an older Arcus 11:38 (2018).

### The record

- **TheRetroRunner, 11:32.183**, run z5pwrgdm.
- Submitted 2023-08-05 00:22 UTC, verified 2023-08-05 by examiner `jpr2q658`.
- NES console, USA/NTSC. The VOD was created 2023-08-04 21:18 UTC.
- His comment: "6-2. That's it. Been doing this long enough to know not to say I'm done forever, but it's getting pretty close to my max potential. Without the missed manip, maybe a low 31 or high 30, but I am the most proud of this record out of all of them. By all accounts, should have missed the plate kill, missing 2 slashes, but we somehow willed it to happen. We fought hard for this one."
- **Timed on its own video [measured]:** START = Ryu first visible (video frame 1707); END = TIMER-000 first shown (43238). Span 41,531 frames at 60 fps = 692.1833 s, **exactly the claimed time**. That is 41,599 +/- 2 NES frames.
- Splits for all 22 stages and 8 boss kills, the comparison with the TAS, and the method are in `record_notes.md` and `record_events.json`.

## 3. TAS

Full detail in `tas_notes.md`.
- **Current:** TASVideos **4751M**, "NES Ninja Gaiden by eien86 & Scumtron in 10:50.33".
  - BizHawk 2.8 NesHawk, our exact ROM, 39,084 frames, power-on start. Published 2022-07-06 (submission 7532S).
  - Video: https://www.youtube.com/watch?v=z1AnlaNmCyI. Movie: `dl/tas/4751M/`.
- **It syncs in our BizHawk 2.11.1** [replay]: the stage and room changes land on the frames in its own timing table.
- **Under the board clock it is 10:54.78** (RAM frames 174 to 39,525). That is 37.4 s under the record.
  - TASVideos stops its clock at the last input (the demon's HP display reaching 0). The board waits out the 147-second timer tally, 441 frames.
- **It is not legal for the board:** 131 Left+Right events (1,221 frames) and 1,778 Up+Down events (3,430 frames). Every NES Ninja Gaiden publication uses these combos.
- Other branches: "pacifist" 4812M 11:16.89; "damageless" 7355M 10:56.203, which uses the JP ROM. Obsoleted: 3223M 10:50.36 (FCEUX fm2 with 84 lines of technical notes) and older FCEU movies back to 2004.

## 4. Game knowledge

See `game_mechanics.md` for:
- 6 acts and 22 stages, rooms;
- the Act VI return-to-6-1 rule;
- the timer and tally (3 frames per second left; the sub-timer carries over);
- movement constants, wall climbing, sticky floors;
- sword and slash cancel, the first-slash quirk, sub-weapons and their ninpo costs;
- weapon persistence across rooms;
- damage boosts, `$BF` tossers, inherited subpixels, spawn iterator, draw interrupts, birds, bats, cheetahs, Tysons;
- pre-kill, skywalk;
- the RTA 5-1 manip and the Jaquio plate kill;
- lag (only 32 lag frames in the whole TAS, all at transitions).

RAM: `ram_map.md`.

## 5. Sources (URLs)

speedrun.com:
- Game: https://www.speedrun.com/ngnes. Record: https://www.speedrun.com/ngnes/runs/z5pwrgdm
- API endpoints: section 2.
- General NES rules doc: https://docs.google.com/document/d/1apP69VDIzUx-iVO_sj5YjTxBAE2ukHPa6kl33AOW9hA (via https://goo.gl/pYN6AR)
- Guides (videos, not watched):
  - Arcus Advanced https://www.youtube.com/watch?v=x-cyeYr5bTI and Beginner https://www.youtube.com/watch?v=AJkCsI9nj04
  - Sinister1 https://www.youtube.com/watch?v=GqKyAp_rU5M and https://www.youtube.com/watch?v=Z-MBNmAobdU
  - Jaquio all strats (TheRetroRunner) https://youtu.be/s-A6dsb1MWQ
  - ShuriBear 2020 any% https://youtu.be/_eMHhSLrDmQ
  - Duckfist sword canceling https://www.youtube.com/watch?v=ylKs_JnBXuw
  - twin0mega wall climb https://www.twitch.tv/videos/310179594
- Resources (download blocked by a Cloudflare challenge for scripts; open them in a browser if needed):
  - maps (NESmaps) `/static/resource/6e1cr.zip`
  - autosplitter `d6x1v.asl`
  - hitbox Lua `xp7f4`, `het3o`, `go29z`
  - Practice ROM v4.02 `jwrxg`
  - Ninja Gymnasium `4hhdk`
  - MashyMashy `qujir` and `24bvi`
  - FCEUX states `ct710`
  - Demon Head ROM `18d1t`
  - Discord https://discord.gg/NEWA2xg

TASVideos:
- Game 175: https://tasvideos.org/175G. Resources: https://tasvideos.org/GameResources/NES/NinjaGaiden
- Movies: https://tasvideos.org/4751M (current), https://tasvideos.org/3223M, https://tasvideos.org/562M, https://tasvideos.org/4812M (pacifist), https://tasvideos.org/7355M (damageless)
- Submissions: https://tasvideos.org/7532S, https://tasvideos.org/5222S, https://tasvideos.org/1119S, https://tasvideos.org/1081S, https://tasvideos.org/986S, https://tasvideos.org/7602S, https://tasvideos.org/10688S (text copies in `dl/tas/text/`)
- Bird simulator: https://tasvideos.org/UserFiles/Info/637923955744472700
- Jaffar bot: https://github.com/SergioMartin86/jaffar
- Pre-kill: https://www.twitch.tv/videos/1497514873. Skywalk: https://www.youtube.com/watch?v=rIMaGYevbhk

Code:
- Disassembly: https://github.com/0xe1f/NinjaGaidenNES (cloned to `dl/NinjaGaidenNES`). Byte-exact, US ROM; bank 07 fully source; docs in `docs/game-notes.md` and `docs/progress.md`.
- Autosplitter: https://github.com/BroDMax/NinjaGaiden-NES-autosplitter (cloned to `dl/NinjaGaiden-NES-autosplitter`)

Other:
- https://articles.retroware.com/2021/02/04/streamer-completes-world-first-100-damageless-run-of-ninja-gaiden/ (human mashing anecdote)
- https://www.guinnessworldrecords.com/world-records/555176-fastest-completion-of-ninja-gaiden-on-the-nes-any (old 11:38)

## 6. Open questions and next steps

1. **On-screen offsets for the clock.** Ryu is drawn some frames after `$33 == 0x97`, and TIMER-000 is drawn some frames after `$63 == 0`. Measure both by screenshot in BizHawk; this is a harness job. The record shows the timer digits only on odd values, 6 frames each, so the HUD timer may be redrawn on a cycle.
2. **Human-legal wall-climb routes.** The TAS's routes in 2-1, 2-2, 4-3, 5-x, 6-2 and 6-3 use L+R or U+D+L. The record's routes (video in `dl/record_video/`) and the speedrun.com guide videos show the legal alternatives. A bot search with L+R and U+D forbidden should beat both.
3. **Press cap.** No direct measurement is possible from this record. Consider checking other top runs (Arcus, blacksquall, Lainerainer) for a handcam or clear controller audio.
4. **Sub-timer phase per boss.** Plan the entry sub-timer windows so that every boss tally loses a second. The TASVideos formula is in `game_mechanics.md` section 2.
5. **Pre-kill and the tosser gatekeepers.** These could turn the TAS's "false frames" into real ones in a legal run.
