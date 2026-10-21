# Final builder (routes `up17`, `up17_*`): notes, 2026-10-10 10:07 - 12:45

Owner of this file: the final builder. Files: `u17f_*.py`, `logs/fix/u17f_*`, segments `logs/pbeam_Fk*.json`
(the older `pbeam_F2W` / `F5*` files are NOT mine), bookmarks `states/Fk*.State` and `states/u17f_*`, routes `up17`, `up17_*`.
All commands from `../toads`, `TOADS_CORE` unset (quickerNES only: the NesHawk port is still to do).
Nothing here writes memory. No file of another owner was edited; T12a (TOWER1) and the C / A / K segments are used as they are.

## 0. Result

**`up17` = RUN TIME 11:54.02, T. Bird cut on frame 44,986** (landing 2074; up16b2: 45,425; track C's up17a2: 45,261).

    python assemble.py up17 Fk1b Fk3b Fk3t Fk4u Fk6v Fk8u Fk9u Fk10u A11r T12a A13r_k0p16 > logs/fix/u17f_assemble_up17.txt

`up17: 44986 frames, timing starts at 2074, ... replay MATCH sha1 cfa6cb83`
`up17: RUN TIME 11:54.02 = 42912 frames (landing 2074 -> cut to Professor T. Bird 44986); queen_speech_cut 44566 (reference
only: the old, wrong finish); record 12:29.25 = T. Bird cut at <= 47102 for a landing at 2074 -> UNDER the record by 35.23s`

- Input file `logs/up17.inputs.txt` (copy `logs/fix/u17f_up17_x_44986.inputs.txt`), sha1 2344f9b48fdfbb2e13209f9aef4fb6bf53c6a1b2.
- RAM sha1 after the last input cfa6cb83. It is NOT the A lineage's 91a0c7b3: behind the new tower the Queen's entry differs in
  `$0C` (29 / 157: the tower is 256 timer ticks shorter) and the ending after the speech rolls other dice; the end RAM differs
  from A13r_k0p16's own in `$25-$28`, `$75`, `$CE` only (`u17f_enddiff.py`). Toad, health, lives, score identical on every
  frame of the Queen segment; both cuts on the old frames (1601, 2021).
- Banned-press scan (`python u16v_scan.py logs/up17.inputs.txt <segments>` -> `logs/fix/u17f_scan_up17.txt`): Left+Right 0,
  Up+Down 0, unknown tokens 0, Start 4 (title, frames 1171-1174), Select 206 frames (Fk1b 1, Fk4u 2, Fk6v 1, Fk8u 38, Fk9u 8,
  Fk10u 1, A11r 20, T12a 54, Queen 81), the file equals intro + the eleven segments frame for frame.
- Third replay by other code (`python u17f_verify.py up17` -> `logs/fix/u17f_verify_up17.txt`): landing 2074, T. Bird cut = the
  last input; lives / health / score when each level ends: 3/47/4000, 2/0/43600, 2/31/86600, 2/47/91600, 3/47/143600,
  3/47/168600, 3/47/179600, 4/47/233800, 4/0/284550, 5/47/334550 = the reference chain's.
- Chain proof (`logs/fix/u17f_chain_up17.out`): every segment against its own reference run, per frame.

Frame budget against track C's up17a2 (45,261) = **-275**:

| piece | frames | segments |
|---|---|---|
| Karnath: track K2's K7 for K6 (-4), then the page behind it 2 shorter | -6 | `Fk6v` |
| Level 1 -> 3 page 200 frames (track C: 202) | -2 | `Fk1b`, `Fk3b` |
| Level 3 -> 4 page 44 frames (was 46) | -2 | `Fk3t`, `Fk4u` (head) |
| Level 4 -> 6 page 4 frames shorter | -4 | `Fk4u` (tail) |
| Level 8: fight f62 (track C's, "can never merge") with a 49-frame page | -4 | `Fk8u` |
| Level 9 -> 10 page 2 frames shorter, Rat Race re-phased | -2 | `Fk9u`, `Fk10u` |
| Tower: TOWER1's T12a (8,153) for A12r (8,408), Queen A13r_k0p16 unchanged behind it | -255 | `T12a` |

Verified routes on the way (assemble.py, two power-on replays MATCH each; logs `logs/fix/u17f_assemble_<route>_<cut>.txt`, input
copies `logs/fix/u17f_<route>_<cut>.inputs.txt`): up17 first build = up17a2's segments 45,261 (sha1 91a0c7b3) -> up17_k2 45,259 ->
up17_k4 45,257 -> up17_h 45,255 -> up17_t 45,009 (T12x + L13_L12h_k0, sha1 10722e85) -> up17_ta 45,000 (T12a + A13r_k0p16,
sha1 cfa6cb83 from here on) -> up17_u 44,998 -> up17_v 44,992 -> up17_w 44,990 -> up17_x = up17 44,986.

## 1. The method that found all of it

**A card page between two levels is not a fixed length, and the hidden alignment is moved by ANY button, not only Select.**

- Where the alignment comes from (disassembly, `python u17f_dis.py 0 8700 8760`, `... 0 FE74 FFB3`): when a frame's work is done the
  game sits in `$871F: JSR $8728 / JSR $8743 / JMP $871F`, stirring the dice `$25-$28` (with `$0B`, the toad's x `$3FD`, `$457`,
  `$41B`) until the next NMI; the NMI handler (`$FF98` -> `$FE75`) throws the stack away and jumps to the frame routine through
  `($0023)`. The dice a frame sees are whatever the stirring loop (213 CPU cycles a lap) had reached when the NMI cut it. So the
  alignment = on which CPU cycle the previous frame's work ended, and every input that makes a frame's work a cycle longer or
  shorter moves it for good.
- A page's length depends on the alignment it is entered with (extra load frames): measured ranges, in frames from 5 inputs
  before the level byte turns 254 to the placement: 4 -> 6: 48..53, 6 -> 8: 46..56, 8 -> 9: 48..54, 9 -> 10: 50..59,
  10 -> 11: 47..52, 11 -> 12: 48..52; Level 1 -> 3 from the warp: 200..204; 3 -> 4: 43..47.
- An A,B mash on every frame is not the shortest way through a page: a card can refuse the button of the mash's phase for a
  frame, and the third card shows a press only one frame later. The shortest is three single presses, found per state by
  pressing each card on the first frame it reacts (`u17f_head.py` with `U17F_GREEDY=1`; checked against the breadth-first
  search `u17f_bfs.py`: same lengths).
- So the search is: ONE extra press of any of the seven legal buttons on a frame of the level before the page (in play, in a
  death, in a warp animation), the page pressed card by card, and then the test every chain used: the next segment's frames
  8..240 RAM-identical to its reference AND the alignment 240 frames in equal. When the natural page comes out an odd number
  of frames off, the three "one card answered a frame late" pages are tried too.
- **Levels that do not read the dice** (toad, health, lives, score identical on every frame under other dice; only `$25-$28`,
  `$75` differ): Level 3 Turbo Tunnel (`logs/fix/u17f_cmp_L3free.txt`, also one frame early: `u17f_cmp_L3odd.txt`), Level 6
  Karnath's Lair (`logs/fix/u17f_cmp_L6free_sel.txt`: identical for 2,420 frames, only the page behind it moves), Level 10 Rat Race
  (`logs/fix/u17f_cmpbm_L10free2.txt`). Behind such a level only the NEXT dice level's placement has to be in phase, so the page
  in front of it can be made as short as its alignment range allows (`U17F_FREE=1`: accepted when the placement RAM equals the
  reference's outside dice / timers / pad bytes) and the page behind it repairs parity and phase. Levels 4, 8, 9, 11, 12, 13 do
  read the dice.
- An odd shift never merges into a dice level. Every pair of pages around a dice-free level therefore has to sum to an even
  change: (1 -> 3, 3 -> 4) = (200, 44) with floors (200, 43); (4 -> 6, 6 -> 8) = (48, 46), both floors; (9 -> 10, 10 -> 11) =
  (50, 48) with floors (50, 47). 11 -> 12 stands at 49 with floor 48 (odd, Levels 11 and 12 both read the dice).

## 2. Segment by segment (index = position in the segment; all presses are single frames)

| segment | what it is | inputs | proof |
|---|---|---|---|
| `Fk1b` | `C1b` + B on index 3 (during the descent, before the landing): the Level 1 -> 3 page then takes 200 frames | 395 | `logs/fix/u17f_head_Fk3g.out` |
| `Fk3b` | `C3u` with a 200-frame head: A on 165, B on 175, A on 188 | 1,820 | Level 3 is dice-free |
| `Fk3t` | `L3skipu` + Left on index 297: repairs the Level 4 placement behind the shorter page (PC `$86B4` ts 15 parity 1, merged) | 596 | `logs/fix/u17f_head_Fk4e3.out`; Level 3 still ends 2 lives / 0 health / 43600 |
| `Fk4u` | head A on 9, B on 19, A on 32 (44 frames) + `B4`'s inputs after its placement, + Select on index 4683 (in play), + the Level 4 -> 6 page as three presses on 5113 / 5123 / 5136 (48 frames from index 5100, was 52) | 5,148 | `logs/fix/u17f_head_Fk4p1.out`; power-on bookmark `Fk4u_end0`: Level 4 ends 2 / 31 / 86600, toad set down on frame 9876 |
| `Fk6v` | K2's `K7` up to index 2415 + Select on index 2231 (warp room, in play) + page B on 2426, A on 2436, B on 2449 (46 frames from 2415, K7's was 48): Level 8 placement PC `$84CB` ts 15 = the reference's | 2,461 | `logs/fix/u17f_head_Fk6q1.out`; `Fk6v_end0` = `C6_end0`, 0 RAM bytes differ |
| `Fk8u` | track C's raw build `C8f62_raw` (climb C4 + fight f62, kill + death 1075) up to index 3824 + Select on 3408 (boss's death) + page A on 3838, B on 3848, A on 3861 (49 frames): Terra Tubes placement PC `$84B1` ts 10 = A9r's reference exactly | 3,873 (C8c 3,877) | `logs/fix/u17f_head_Fk8f1.out`; Level 8 ends 3 / 47 / 143600 |
| `Fk9u` | `A9r` + Up on index 9380 (9 frames before the toad dies on the last spikes) + page A on 9748, B on 9758, A on 9771 (50 frames from 9735, was 52) | 9,785 | `logs/fix/u17f_head_Fk9f1.out` |
| `Fk10u` | `A10r` + Select on index 60 + page A on 1906, B on 1916, A on 1929: Clinger-Winger placement PC `$84EA` ts 20, merged | 1,941 | `logs/fix/u17f_head_Fk10r2.out` |
| `A11r` | chain A's, unchanged | 6,876 | |
| `T12a` | TOWER1's tower as it stands (NOT `T12x`: T12x carries one Select that phases it onto the OLD Queen `L13_L12h_k0`; T12a itself is already in phase with `A13r_k0p16`: `logs/fix/u17f_syncnext_Fk12y.out`, "IN SYNC ALREADY") | 8,153 | level 12 ends 4 lives / 284550 |
| `A13r_k0p16` | chain A's Queen + ending, unchanged; T. Bird cut on its last input | 2,021 | |

Why fight f62 merges after all (track C's notes say it never can): with the page pressed card by card its natural length behind
f62 is 48 or 49 frames, and the 49-frame one lands in A9r's class and parity (`$84B1` ts 10 or 25). Track C's A,B mash could not
produce that page. Kill + death + page: C8c 1077 + 51 = 1128, Fk8u 1075 + 49 = 1124 (page counted from 5 inputs before the 254).
Behind C8c itself no 49-frame page merges (495 variants: classes 0 and 1 only) - the gain needs the 1075 fight.

## 3. What was tried and gave nothing (do not repeat)

- Level 11 -> 12 (`logs/fix/u17f_head_Fk11q.out`, 2,007 variants, all buttons, last 300 frames): 49 (as built) merges, the natural
  48 is odd, 47 never appears.
- Level 10 -> 11 behind the old chain and behind `Fk9u`: 48 merges, 47 is odd, 46 never appears.
- Level 9 -> 10 in strict mode (`u17f_head_Fk9q.out`): the 50-frame pages do not merge into Rat Race's reference RAM - they
  do not have to, Rat Race is dice-free (that is how `Fk9u` + `Fk10u` came about).
- Level 3 -> 4 behind the 201-frame Level 3 head (`u17f_head_Fk4o.out`): 43-frame pages exist but never in phase; 45 merges
  (same total as now).
- The Queen's ending (`u17f_end.py`, 980 variants: one press of any button on indices 1452-1600 of A13r_k0p16, speech answered
  on its first frame): T. Bird cut 2021 (speech 9 frames) is the minimum; the others give 2022-2024.
- Fixed-mash tail scans of A9r / A10r / A11r with all buttons (`u17f_sync_Fk9s/10s/11s.out`): nothing shorter in sync.
- K7's own page with button / hold / delay variants (`u17f_page_Fk6p.txt`, 1,728 variants): nothing at 2,463 in phase.

## 4. Open (small)

- One odd frame is left at four places: 3 -> 4 (43), 8 -> 9 (48), 10 -> 11 (47), 11 -> 12 (48). Each needs a second odd change
  inside the same dice-free span, and there is none left. Two frames more would bring the run under 11:54.00.
- A Level 8 fight with kill + death two frames under 1075 would pay again in full.
- K2's "about 19 frames" in Karnath's room 1 now pay 1 : 1 (Level 6 is dice-free; only the page behind it needs a re-phase:
  `U17F_GREEDY=1 U17F_REFBEFORE=... U17F_REFPREV=Fkx6a python u17f_head.py <chain> <Level 6 up to 5 inputs before the 254> Fkx6b 7 <tag> 200 <buttons>`).
- The route still contains A,B mashes on every frame in the stretches where no input is read (warp animations, deaths:
  route frames 9658-9829, 16023-16162, 25851-25946, 27793-27889, 34669-34813). The de-mashed release list has to be rebuilt
  and re-verified for this route: with the alignment this sensitive, do not assume removing a press is harmless.
- NesHawk port not done.

## 5. Tools (all `u17f_*.py`; copies of other owners' tools carry my prefix)

`u17f_lib.py` (track C's lib), `u17f_head.py` (the main tool: page at a segment's head or - with pseudo-segments `Fkx<level>a` =
level up to 5 inputs before the 254, `Fkx<level>b` = the rest + the next segment's first 400 inputs - at its end; power-on replay
to the true state; env `U17F_GREEDY`, `U17F_FREE`, `U17F_REFBEFORE`, `U17F_REFPREV`, `U17F_GSKIP`, `U17F_STEP`, `U17F_LO/HI`,
`U17F_HEADS`, `U17F_HEADLEN`; results cached per page-entry state), `u17f_headmk.py`, `u17f_bfs.py` (BFS of a page),
`u17f_sync.py` / `u17f_mk.py` / `u17f_chain.py` / `u17f_poweron.py` (track C's sync / mk / chain / poweron), `u17f_page.py`
(page-mash variants at a segment's end), `u17f_syncnext.py` (chain A's), `u17f_verify.py` (chain A's third replay),
`u17f_end.py` (ending scan), `u17f_cmp.py` / `u17f_cmpbm.py` (is a level dice-free), `u17f_enddiff.py`, `u17f_segend.py`,
`u17f_cls.py`, `u17f_lv.py`, `u17f_pagetrace.py`, `u17f_greedytest.py`, `u17f_dis.py` (6502 disassembler for the PRG).
Probe-only segments (never in a route): `Fkx*`, `Fk6i2`, `Fk6b`, `Fk6e1a/b`, `Fk6p`, `Fk3s`, `Fk4`, `Fk3o`, `Fk4t`, `Fk9s`,
`Fk10s`, `Fk11s`, `Fk9w`, `Fk12y` (= T12a + one Select, not needed). Bookmarks: `Fk3s_end0`, `Fk3t_end0`, `Fk4u_end0`,
`Fk6v_end0` (power-on replays), `Fk9u_end0b`, `u17f_T12a_end` (tool-made).
