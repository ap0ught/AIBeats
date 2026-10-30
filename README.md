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

## Repository layout

- `zelda/` — Zelda harness, journal, and run.
- `battletoads/` — Battletoads harness, journal, and run.
- `contra/` — Contra harness, journal, and run.
- `releases/` — original release zips for each game.
- `releases/release_battletoads.zip` came from https://github.com/bearsgaming-ui/AIBeatsBattletoads2.
- `releases/release_battletoads_original.zip` came from https://github.com/bearsgaming-ui/AIBeatsBattletoads.
- `releases/release_contra.zip` came from https://github.com/bearsgaming-ui/AI-Beats-Contra.

## Notes

- Runs are tool-assisted: built with save states and search, played back in an emulator (BizHawk 2.11.1).
- Nothing here plays without your own copy of the cartridge; ROMs are deliberately excluded.


## ROMs

ROMs are not committed. Each game's `roms/` directory documents the expected filename and hash:
- `zelda/roms/README.md`
- `battletoads/roms/README.md`
- `contra/roms/README.md`

Copy your own dump into the matching `roms/` folder; `.gitignore` keeps `*.nes` out of git.
