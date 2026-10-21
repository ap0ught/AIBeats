# Battletoads video: how it's built

Everything in the video is made from this project's own data: the real captures, the per-frame RAM and sprite
memory of the verified run (`logs/cap14.ram/.oam`, which replayed to the same sha1 e2a1d2dc), the search
recordings, the journal and the token log. The sound effects and the music are synthesised in `audio.py`
(original chiptune), so there's no third-party audio.

| section | what's on screen | source |
|---|---|---|
| 01 | Opening montage, cut to the beat: a 24-emulator grid of Turbo Tunnel attempts, then the bike, the swim, Clinger-Winger, the rat boot, a spring pump, the big boot and the Queen's last hit; then the title card | `montage.py`, `gridshot.py`, `charts.py title_card` |
| 02 | Zelda best-of (grid, planner lines, blue Darknuts, route map), your comments slamming in, "warps or no warps?", SO WE DID BATTLETOADS, subscribe click | `s02.py` |
| 03 | IS IT EVEN POSSIBLE?, the Turbo Tunnel, the record card, the rules and goals | `sections.py s03`, `charts.py` |
| 04 | How to read the screen: the run panel, highlighted one part at a time | `sections.py s04` |
| 05 | DAY 1: POWER ON, button experiments, the press-Start-on-every-frame grid, RAM vision, research day, Level 1, the 228 jumps the search tried, the architecture | `sections.py s05`, `explainers.py` |
| 06 | GOAL ONE: the rats win at first, every level of the first finished run with callouts, the tower fall grid, DAY 5: 18:04.08 | `sections.py s06` |
| 07 | GOAL TWO: where the time went, the bike skip memory walk, intro skips, RNG chaos, the stitched-tower ghost race, the progression chart, 12:28.60 RECORD BEATEN, 12:23.39, integrity checks | `sections.py s07`, `towerrace.py`, `charts.py`, `explainers.py` |
| 08 | What's a TAS? | `charts.py tas` |
| 09 | Claude, by the numbers; what the tokens went on | `charts.py` |
| 10 | The full run from power-on at 1080p, with level slams, credit cards and target tracking | `run1080.py`, `run_cues.json` |
| 11 | Thank-yous, two calls to action, end screen | `sections.py s11` |

**Narration:** record from `VOICE_SCRIPT.md`, one file per section, into `yt/voice/`. Each section's picture is
then fitted to the length of your read. Burned-in captions are never used; an `.srt` gets generated from your audio.

**Rebuild:** run `python sections.py s03 s05 …` (it skips pieces that already exist, and `FORCE=1` re-renders),
then `python cut.py draft`.
