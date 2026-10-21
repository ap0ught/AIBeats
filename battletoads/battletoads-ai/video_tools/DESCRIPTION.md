# YouTube description (draft)

An AI taught itself to speedrun Battletoads, one of the hardest games on the NES, under the human speedrun rules,
and finished in 12:23.39. The human world record is 12:29.25.

Last time it was Zelda. You asked for Battletoads.

How it works: Claude (Anthropic), working in Claude Code, wrote its own tools. It built a bridge into the BizHawk emulator,
mapped the game's memory, and wrote search programs that tried millions of input sequences. The final run is a file of
46,751 button presses played back from power-on, and every route was verified by replaying it twice and matching the
console's memory exactly.

The rules it kept: speedrun.com Battletoads (NES), Any% (No Credits Warp). No credits warp, no Left+Right or Up+Down
presses, no turbo, and the clock starts when the toad lands. Because it was built with save states and search, it is a
tool-assisted run (TAS), not a human run, so it can't go on the human leaderboard.

## Chapters
(filled in from the final cut)

## Thank you
- jay_cee: the 12:29.25 world record. https://www.speedrun.com/battletoads_nes
- jc583: run notes on Speed Demos Archive. https://speeddemosarchive.com/Battletoads.html
- TASVideos authors: feos, Alyosha & Samsara; Lobsterzelda; MESHUGGAH & Koh1fds; Phil & Genisto. https://tasvideos.org/66G
- feos's disassembly and Lua tools, and the DataCrystal RAM map
- BizHawk (TASVideos)
- Battletoads © 1991 Rare / Tradewest

## Notes
- The narration is my own voice. All the graphics are drawn from the run's own data: the per-frame memory of the
  verified run, the search recordings, and the AI's journal.
- The music and sound effects are original, synthesised for this video.
- Tokens: about 3.03 billion over 12 days and 5,388 AI replies, about $1,327 at API list prices.
