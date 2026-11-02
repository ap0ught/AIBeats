# AI Beats

A collection of AI-played (tool-assisted) NES runs by Bears Gaming Den. Each game lives in its own folder with the
harness, journal, knowledge notes, and the final input movie. Game ROMs are not included; bring your own.

## Games

### Zelda — `zelda/`
- Run: 37:02 from power-on to Zelda, no glitches, no memory editing, no human input.
- Video: [I Gave an AI Zelda and One Rule: Don't Cheat.](https://www.youtube.com/watch?v=mBalZml520o&t=116s)
- Entry point: `fullgame.py`, `route4.py`; player code in `zelda/`.

### Battletoads — `battletoads/`
- Run: 11:54.02 (corrected; earlier published run was 12:31.75).
- Video: [I Was Wrong. So the AI Went Back and Beat the Battletoads World Record by 35 Seconds.](https://www.youtube.com/watch?v=EvFIxPDFqTc)
- Original run video: [AI Taught Itself Battletoads in 12 Days and Beat the Record](https://www.youtube.com/watch?v=5-U0If9Gixg)
- Entry point: `README.md` in the folder; run inputs in `run/`.

### Contra — `contra/`
- Run: 9:24.321 (33,915 NES frames), 23.86 s under the human record.
- Video: [An AI Beat Contra's World Record by 24 Seconds](https://www.youtube.com/watch?v=OaePvbX8jqw)
- Entry point: `README.md` in the folder; harness in `harness/`.

### Ninja Gaiden — `release_ninja_gaiden/`
- Run: 11:25, 6.5 s under the 11:32 human record.
- Video: [Can AI Beat the World Record of Ninja Gaiden (NES)?](https://www.youtube.com/watch?v=VTVDW15C1C8)
- Full uncompressed release imported from [`AIPlaysNinjaGaiden`](https://github.com/bearsgaming-ui/AIPlaysNinjaGaiden), including the harness, knowledge notes, run artifacts, verification data, and final input movie.
- Entry point: `release_ninja_gaiden/README.md`.

## Repository layout

- `zelda/` — Zelda harness, journal, and run.
- `battletoads/` — Battletoads harness, journal, and run.
- `contra/` — Contra harness, journal, and run.
- `release_ninja_gaiden/` — uncompressed contents of `release_ninja_gaiden.zip`, including the Ninja Gaiden AI harness and verification artifacts.
- `releases/` — original release zips.
- The Ninja Gaiden source archive `release_ninja_gaiden.zip` came from https://github.com/bearsgaming-ui/AIPlaysNinjaGaiden and was unpacked into `release_ninja_gaiden/` rather than committed as a second copy.
- `releases/release_battletoads.zip` came from https://github.com/bearsgaming-ui/AIBeatsBattletoads2.
- `releases/release_battletoads_original.zip` came from https://github.com/bearsgaming-ui/AIBeatsBattletoads.
- `releases/release_contra.zip` came from https://github.com/bearsgaming-ui/AI-Beats-Contra.
- `releases/release_zelda.zip` came from https://github.com/bearsgaming-ui/AIBeatsZelda/blob/main/release.zip.

## Notes

- Runs are tool-assisted: built with save states and search, played back in an emulator (BizHawk 2.11.1).
- The Ninja Gaiden release directory is the uncompressed contents of `release_ninja_gaiden.zip`; the source archive remains available in [`AIPlaysNinjaGaiden`](https://github.com/bearsgaming-ui/AIPlaysNinjaGaiden).
- Nothing here plays without your own copy of the cartridge; ROMs are deliberately excluded.


## ROMs

ROMs are not committed. Each game's `roms/` directory documents the expected filename and hash:
- `zelda/roms/README.md`
- `battletoads/roms/README.md`
- `contra/roms/README.md`
- `release_ninja_gaiden/` — use the ROM requirements documented in `release_ninja_gaiden/README.md`.

Copy your own dump into the matching game's documented location; `.gitignore` keeps `*.nes` out of git.
