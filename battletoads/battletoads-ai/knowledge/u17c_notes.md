# Track C (integration, routes up17a*): Karnath K6 + Level 8 + the A9r lineage in one route - working notes

> **BEST (08:48): `up17a2` VERIFIED = RUN TIME 11:58.60, T. Bird cut 45,261** (up16b2: 45,425; -164).
> `python assemble.py up17a2 C1b C3u L3skipu B4 C6 C8c A9r A10r A11r A12r A13r_k0p16` (section 5). Read section 4 before
> building anything in front of a level load: the hidden alignment has a period of 6 frames, not 2.

Started 2026-10-10 07:24 (local). Owner of this file: track C. Files: `u17c_*.py`, `logs/fix/u17c_*`, segments
`logs/pbeam_C*.json`, bookmarks `states/C*.State`, routes `up17a*`. Nothing here writes memory. `TOADS_CORE` unset.

## 1. Level 6: `C6` = K6 behind B4, in the phase of the old Level 8 entry (DONE 07:32)

- `python u17c_chain.py B4_K6 B4 K6` (`logs/fix/u17c_chain_B4_K6.txt`): K6 (2,467 inputs, made from `L4c5_end0`) replays
  behind `B4` (the 4 -> 6 page mashed A,B, -2) with the toad identical on every frame; only frames 1-6 of Karnath differ in
  a timer byte; end RAM identical (sha1 0f56db25 = K6's own power-on hash). So K6 goes behind B4 as it is.
- **Which clock is the tower bound to?** `python u17c_probe1.py B8h_K6 B8_h L6c_end0 K6_end0`
  (`logs/fix/u17c_probe1_B8h_K6.txt`): at the Level 8 placement the RAM behind K6 differs from the old entry in `$0B` and
  `$1A` only; three frames later (Level 8 frames 4, 5, 6) **the whole RAM is identical, 0 bytes differ** (stack page aside).
  Nothing that kept running through Level 6 survives the level load: every clock the tower uses (`$0B/$0C` and all object
  timers) restarts at the load, so the gates stand exactly as in the old lineage relative to the placement. What differs
  from frame 7 on is the dice (`$25-$28`, `$75`, the `$740` table) = the hidden CPU alignment, nothing else. With K6 as built
  the old climb tracks for 1,187 frames and then takes a hit (hp 43 on frame 1188): the climb DOES use the dice.
- So the job is only the alignment: `python u17c_sync.py K6@B4_end0 B8_h 2252 7 C6` (`logs/fix/u17c_sync_C6.txt`; copy of
  chain B's `u16b_sync.py`). Reference `B8_h` from `L6c_end0`: entry PC `$84CB` timestamp 15. K6 as built: PC `$84CD` ts 10.
  Presses during the warp animation (the 180 idle frames after the portal touch) change nothing (300 variants, one
  alignment); **one Select / Up / Down on segment index 2431, the frame before the page's first A, gives PC `$84CB` ts 15 =
  the reference's alignment exactly**. `C6` = K6 + Select on index 2431: 2,467 inputs, no Start, 1 Select.
- Power-on: `python u17c_poweron.py C6_end0 L1b L3u L3skipu B4 C6 --cmp C6_end0b --lvl 7`
  (`logs/fix/u17c_poweron_C6_end0.txt`): toad set down in Level 8 on frame **12353** (old 12483; -2 B4, -128 K6), health 47,
  lives 2, score 91600, RAM sha1 d1a87884, 0 bytes from the tool-made bookmark. Bookmark `states/C6_end0.State`.
- `python u17c_chain.py C6_B8h C6@B4_end0 B8_h` (`logs/fix/u17c_chain_C6_B8h.txt`): the old Level 8 `B8_h` replays behind C6
  with only frames 1-3 differing (timer byte), end RAM identical (sha1 1d5b8a09). **No climb re-search and no fight
  re-search were needed: every Level 8 piece searched from `L6c_end0` / `early_L8_p0` is valid behind C6.**

## 2. Level 8 behind C6 and the A9r phase: `C8b` (DONE 07:43)

- Level 8's tail in the phase of `A9r` (reference entry `A8r_end0`: PC `$84B1` timestamp 10, parity 1), tool
  `python u17c_sync.py <raw Level 8>@C6_end0 A9r <kill index> 11 <out>` (one Select / Up / Down on every tail frame):

  | raw segment (chain B's build: climb C4 + fight + 300 idle + A,B) | fight | kill frame (old clock) | death | merged variants | shortest merged |
  |---|---|---|---|---|---|
  | `B8_h_raw` (3,895) | `u16b_fight_C4h` 652, last blow a jump attack | 15889 | 443 | 33 of 1,465, ALL with the 46-frame page | 3,895 (`pbeam_C8`) |
  | `B8_b3_raw` (3,885) | `u16b_fight_C4b3` 648, last blow a ground punch | 15885 | 437 | 203 of 1,447 = every variant with the 44-frame page | **3,883** (`pbeam_C8b3`, `pbeam_C8b`) |
  | `B8d_raw` (3,891) | `u16b_fight_C4a` 648, jump attack | 15885 | 443 | several, 44-frame page | 3,889 (scan stopped by hand) |

  Merging alignments at the Terra Tubes entry for `A9r`: timestamp 10 (exact) and 25; not 0 / 15 / 30 / 40 and nothing on the other
  frame parity. (For the OLD Level 9 it was 60 and 15: that is why chain B could not use the two 648-frame fights; behind the
  A9r lineage they are the best.) `logs/fix/u17c_sync_C8.txt`, `u17c_sync_C8b3.txt`, `u17c_sync_C8a.txt`.
- **`C8b`** = `B8_b3_raw` + Select on segment index 3484, cut on the placement: **3,883 inputs** from `C6_end0`
  (`python u17c_mk.py B8_b3_raw@C6_end0 C8b 11 3484:Select`; `C8b3` from the finished scan is the same thing with Up on 3411).
  10 shorter than chain B's `B8_h` (3,893): the kill 4 frames sooner and the death 6 frames shorter.
- **The boss's death time is his HEIGHT when the last blow lands** (`python u17c_death.py`, `logs/fix/u17c_death.txt`, 12 stored
  fights): the dead body flies up for 160 frames from the floor (h 30..37), 165 from h 72-73, 166 from h 78-79, and the level byte
  leaves 7 exactly 277 frames after the body is gone: 437 / 442 / 443 = 437 + (h - 30) // 8. Kill him while he stands.
- Proof: `python u16a_chk.py C8b A9r A10r A11r A12r A13r_k0p16` (`logs/fix/u16a_chk_C8b.txt`, copy of the output
  `logs/fix/u17c_chk_C8b.out`): entry RAM identical, **0 frames with any RAM difference in all five segments** (EXACT phase), every
  level end = the old chain's (47/3/168600, 47/3/179600, 47/4/233800, -/4/284550, 47/5/334550), T. Bird cut on the Queen
  segment's last input (2021).

## 3. Routes

- **`up17a` VERIFIED (07:44)**: `python assemble.py up17a L1b L3u L3skipu B4 C6 C8b A9r A10r A11r A12r A13r_k0p16 >
  logs/fix/u17c_assemble_up17a.txt` ->
  `up17a: 45269 frames, timing starts at 2074, ... replay MATCH sha1 91a0c7b3`,
  `up17a: RUN TIME 11:58.73 = 43195 frames (landing 2074 -> cut to Professor T. Bird 45269); queen_speech_cut 44849 (reference
  only: the old, wrong finish); record 12:29.25 = T. Bird cut at <= 47102 for a landing at 2074 -> UNDER the record by 30.52s`.
  Copies: `logs/fix/u17c_assemble_up17a_45269.txt`, `logs/fix/u17c_up17a_45269.inputs.txt` (sha1 0f1bf539...).
  Scan (`logs/fix/u17c_scan_up17a.txt`): Left+Right 0, Up+Down 0, unknown buttons 0, Start 4 (the title, frames 1171-1174), Select 217
  (B4 1, C6 1, C8b 49, A9r 8, A11r 20, A12r 57, Queen 81); the file equals intro + the segments.
  Against up16b2 (45,425): Karnath K6 -128, the A9r lineage -18, fight b3 for h -10 = **-156**.
- `up17a0` VERIFIED (07:36; the fallback on the old lineage): `python assemble.py up17a0 L1b L3u L3skipu B4 C6 B8_h B9
  L9heli_c2L10 L9heli_c2L11s L12h L13_L12h_k0 > logs/fix/u17c_assemble_up17a0.txt` -> `up17a0: RUN TIME 11:59.20 = 43223 frames
  (landing 2074 -> cut to Professor T. Bird 45297)`, replay MATCH sha1 10722e85 (= up16b2 with C6 for B6: -128).

## 4. THE HIDDEN ALIGNMENT, DECODED (what chain B's notes call "not understood"; measured 08:32, `u17c_cls.py`)

`python u17c_cls.py <segment>@<bookmark> <from index> <tag>` writes the core's timestamp after every frame
(`logs/fix/u17c_cls_C8b.tsv`, `_C8f62.tsv`, `_C8h.tsv`). Timestamp `ts` = how far the CPU ran past the frame end, in 1/15 CPU
cycles; `ts mod 15` in {0, 5, 10} = the third-of-a-cycle phase between CPU and picture ("class" 0 / 1 / 2 below).

- **In play the class advances by exactly +1 EVERY frame** (0, 1, 2, 0, 1, 2 ...; lag frames included: every frame is the
  same length for the core). So the alignment has a period of THREE frames, and together with the frame parity the tools
  compare (core frame counter bit 0) a period of SIX. A rebuilt stretch of play merges with the old run behind it only if it is
  **a multiple of 6 frames** longer or shorter. (Chain B's "even shift" rule is the weaker half of this.)
- On the page between two levels there is ONE irregular frame, the frame the new level byte appears (PC `$DADA`): the class
  jumps by +2 there. Frames spent WAITING on a card (mash started late) come in pairs that leave the class alone: padding the
  page by waiting never changes the class (`u17c_tail.py`, `logs/fix/u17c_tail_C8f62.txt`: 44 / 46 / 48 / 50-frame pages by
  a later mash all keep the class). The page lengths the dice give (43-47 after Level 8, steered by a press in the boss's
  death) are LOAD frames and count like play: +2 frames = class +2.
- Consequence for Level 8 -> Terra Tubes in the A9r phase (reference entry: class 2, parity 1). With climb C4 (control on
  segment index 2754) the placement merges only when
  **(fight frames + death + page) = 1085 + 44 (mod 6)**, the page being 44 or 46 (dice):

  | fight | kill + death | page that merges | segment | status |
  |---|---|---|---|---|
  | b3 (648 + 437 = 1085) | = 1085 (mod 6) | 44 | 3,883 | `C8b`, in up17a |
  | a (648 + 443 = 1091) | = 1085 (mod 6) | 44 | 3,889 | merges (scan) |
  | h (652 + 443 = 1095) | = 1083 (mod 6) | 46 | 3,895 | `C8` merges; its 44-frame page (3,893) is the OLD lineage's class |
  | f62 (632 + 443 = 1075), f62r20 (638 + 437) | = 1081 (mod 6) | would need 48: the dice never give it | - | 1,459 variants, none merges (`u17c_sync_C8f62.txt`) |
  | f62r17 (634 + 443 = 1077) | = 1083 (mod 6) | 46 | 3,877 | see section 5 |

  (Section 4.1 counts this more exactly; the table there is the one to use.)
  So a fight is worth `kill + death + 44 + r`, `r = (1085 - kill - death) mod 6`, and only r = 0 or 2 can be built (r = 1 / 3 =
  the 45 / 47-frame pages: other frame parity, not tried; r = 4 / 5 impossible). `u17c_fight.py` ranks its killing blows by that.
  For another climb replace 1085 by the value that makes (control index + fight + death + page) = 2754 + 1085 + 44 (mod 6).
- The same counting explains the pages: at the head of Level 3 two card-wait frames could be removed (section 6) with the
  class unchanged, while Level 8's kill must move in steps of 6.
- What a harmless press (Select / Up / Down while the toad is in play) changes is only the fine part: which instruction the
  frame end falls into (`ts` 10 or 25 merge with A9r, 40 does not). Presses on a page change nothing.

### 4.1 The same thing, counted more exactly (09:45; census of 1,462 tails of fight f63, `logs/fix/u17c_sync_C8f63.txt`)

`u17c_sync.py` now prints (segment length, class, frame parity) for every variant. Behind fight f63 (kill + death 1085, like b3):
3,883 / class 2 / parity 1: 187 variants (ALL merge); 3,884 / class 0 / parity 0: 1,046; 3,884 / class 2 / parity 0: 124;
3,885 / class 1 / parity 1: 105. Read with the per-frame table: **the class counts the PLAY and LOAD frames mod 3; a frame the
card only WAITS for its press adds nothing.** The page after Level 8 is 44 + L + W frames: L = 0, 1 or 2 extra load frames (where
the frame boundary falls inside the load: decided by the alignment itself, steered by a press in the boss's death, and not every
fight offers every L) and W = wait frames (-1 .. +1 by the dice, any number more by starting the mash late). The class at the
placement is K0 + L with K0 = (kill + death - 1085 + 2) mod 3, the parity that of (kill + death + 44 + L + W). The A9r lineage
needs class 2 and an odd total:

| kill + death = c | page that merges | total |
|---|---|---|
| c = 1085 (mod 3), c odd | 44 (L 0) | c + 44 |
| c = 1085 (mod 3), c even | 44 + one wait frame (mash one frame late) - by the counting; not built yet | c + 45 |
| c = 1083 (mod 3), c odd | 46 (L 2) | c + 46 |
| c = 1083 (mod 3), c even | 46 + one wait frame - not built yet | c + 47 |
| c = 1084 (mod 3) | 45 with L 1 (+ a wait frame when c is odd) IF the fight offers L 1: f62 does not (1,459 single presses and 1,200 pairs: classes 0 and 1 only); f63's tails are mostly L 1 | c + 45 / c + 46 |

`u17c_fight.py`'s `pad()` ranks the killing blows by the first four rows and treats the fifth as impossible.
A 45-frame page of the wait kind on the wrong parity tracks the next level for all 240 test frames and is still not merged (the
tool prints -1): chain B's B8a was that case.

## 5. Optional search (07:50-10:10): fights on climb C4, and the route `up17a2`

- `u17c_fight.py <climb json> <tag> [width] [tries] [seed] [fight json] [hits kept]` = chain B's fight beam + chain A's fallback
  tiers and way back out of dead ends; the kill is ranked over ALL killing blows of a generation by
  kill + death + page padding (sections 2 and 4). Results on climb C4 (frames from control; b3 = 648 + 437 is what up17a uses):

  | run | width, tries, seed | kill | last blow, death | kill + death | usable page | segment |
  |---|---|---|---|---|---|---|
  | f61 | 16, 120, 61 | 696 | jump, 443 | 1139 | - | - |
  | f62 | 14, 110, 62 | 632 | jump, 443 | 1075 | none (needs 48) | - |
  | f63 | 18, 100, 63 | 642 | jump, 443 | 1085 | 44 | 3,883 (= C8b, not built) |
  | f62r20 (f62 from its hit 20) | 24, 250, 91 | 638 | ground, 437 | 1075 | none | - |
  | **f62r17** (f62 from its hit 17) | 20, 160, 92 | 634 | jump, 443 | 1077 | 46 | **3,877** |
  | g20 / g18 / g13 (f62 from hit 20 / 18 / 13, padded ranking) | 30,300 / 24,200 / 20,160 | 634 / 636 / 636 | jump 443 / 443 / 442 | 1077 / 1079 / 1078 | 46 / 44 / (45) | 3,877 at best |

  Blows of f62: 26 26 32 38 26 26 26 26 32 38 26 26 26 32 28 28 28 26 32 26 32 26 (floor 26; chain A's t2 on the old climb: 618).
  Behind f62's hit 20 (+574) the 21st blow cannot come before +606 and the kill then falls on 632-638 with the boss in the
  air: every resume ends on kill + death + page = 1123. The next step down is 1117 (kill + death 1073 or 1071): it needs a
  fight 2 frames faster before blow 20, i.e. another fresh seed (40 minutes each next to three other emulators).
- More runs, 08:59-10:10, none better (kill + death + page stays 1123 = `C8c`): fresh seeds h71 (16, 120, 71) 660 / h72 (14, 110, 72)
  658; f62's first 8 blows kept: h81 (18, 120, 81) 660, h82 (16, 130, 82) 660 (both reach blow 21 on +602 / +606 and then lose the
  boss to his fourth take-off); f62's blows 16 / 18 / 19 kept with the corrected ranking and beams of 30-40 x 250-400 tries: j16
  658 + 437 = 1095 (the boss gone after blow 21 on +602), j18 640 + 439 = 1079 (total 1123), j19a 636 + 443 = 1079 (1123).
  Why: the boss takes off about every 170 frames (near +100, +275, +445, +615). 22 blows at the 26-frame floor plus three
  take-offs is about 620, so the fourth take-off meets the last blow: the kill lands on 632-640 with the boss in the air
  (death 439-443) whatever the last five blows do. Chain A's 618 on the old climb got its last blow in 18 frames (toad free 17
  frames after blow 21, Left+A one frame, Left+B the next: an air attack connects at once) BEFORE that take-off; on climb C4 the
  21st blow has not come before +602. A fight under 612 needs a cheaper take-off somewhere (they cost 18 + 18 + 12 here).

- **`C8c`** = `python u16b_build.py logs/fix/u16b_climbC4.json logs/fix/u17c_fight_f62r17.json C8f62r17_raw 300 A` (3,877 as built, 46-frame
  page) + Select on segment index 3421 (`python u17c_mk.py C8f62r17_raw@C6_end0 C8c 11 3421:Select`; scan
  `logs/fix/u17c_sync_C8f62r17.txt`: merged variants from the first tail frames on, timestamps 10 and 25): **3,877 inputs**, 6 fewer than `C8b`.
- **Level 1 -> 3 page, -2** (`u17c_head.py`, `u17c_head2.py`; section 6): `C1b` = `L1b` + Select on index 377, `C3u` = `L3u` with its
  204-frame head (B every other frame) replaced by 202 frames with four presses (A on 166, B on 176, A on 190, A on 201): 1,822 inputs.
- Proof: `python u17c_chain.py up17a2 C1b C3u L3skipu B4 C6 C8c A9r A10r A11r A12r A13r_k0p16` (`logs/fix/u17c_chain_up17a2.txt`): every
  segment against its own reference run: 0 differing frames in C3u, L3skipu, C6, C8c, A9r, A10r, A11r, A12r, A13r_k0p16 (B4: its first
  62 frames differ in the pad bytes, as in every earlier route: its bookmark was saved behind another last input of L3skipu), every
  level end the reference's, T. Bird cut on the last input, final RAM sha1 91a0c7b3.
- **`up17a2` VERIFIED (08:48)**: `python assemble.py up17a2 C1b C3u L3skipu B4 C6 C8c A9r A10r A11r A12r A13r_k0p16 >
  logs/fix/u17c_assemble_up17a2.txt` ->
  `up17a2: 45261 frames, timing starts at 2074, ... replay MATCH sha1 91a0c7b3`,
  `up17a2: RUN TIME 11:58.60 = 43187 frames (landing 2074 -> cut to Professor T. Bird 45261); queen_speech_cut 44841 (reference
  only: the old, wrong finish); record 12:29.25 = T. Bird cut at <= 47102 for a landing at 2074 -> UNDER the record by 30.65s`.
  Copies `logs/fix/u17c_assemble_up17a2_45261.txt`, `logs/fix/u17c_up17a2_45261.inputs.txt` (file sha1 677826e7b7076cf132ad54e52af9b59eb9a04311).
  Scan (`logs/fix/u17c_scan_up17a2.txt`): Left+Right 0, Up+Down 0, unknown buttons 0, Start 4 (title 1171-1174), Select 197 (C1b 1, B4 1,
  C6 1, C8c 28, A9r 8, A11r 20, A12r 57, Queen 81); the file equals intro + the segments.
  Third replay by other code (`python u16a_verify.py up17a2`, `logs/fix/u16a_verify_up17a2.txt`): landing 2074, Queen's speech cut 44841,
  T. Bird cut 45261 = the last input, RAM sha1 91a0c7b3; lives / health / score when each level ends: 3/47/4000, 2/0/43600 (the
  tunnel-skip death), 2/31/86600, 2/47/91600, 3/47/143600, 3/47/168600, 3/47/179600, 4/47/233800, 4/-/284550, 5/47/334550 = the
  reference chain's.
  Against up16b2 (45,425): K6 -128, A9r lineage -18, Level 8 fight and death -16 (b3 -10, f62r17 -6), Level 1 -> 3 page -2 = **-164**.

## 6. Pages at the HEAD of a segment (the cards that were still skipped with one button every other frame)

- `python u17c_head.py <segment> <next level byte> <out>`: breadth-first search over {nothing, A, B} per frame from the segment's
  entry to the placement, then the merge test of every placement with an even gain. `U17C_HEAD_BM=<bookmark>` = the TRUE entry state
  (see the trap below), `U17C_HEAD_NOEXTRA=1` skips the useless extra-press stage (presses on a page do not move the alignment).
- `python u17c_head2.py <previous segment> <segment> <level> <out previous> <out>`: the same heads + ONE Select on one of the previous
  segment's last frames (the toad still in play) to move the fine alignment. `u17c_head3.py`: + one press on the first frames after
  the placement instead.
- Level 1 -> 3 (head of `L3u`): input not read for 157 frames (the warp), placement 204 -> BFS 201 (odd, useless) / 202. With Select
  on `L1b` index 377 the 202-frame head merges exactly (PC `$84ED` ts 5): `C1b` + `C3u`, **-2**, in up17a2.
- Level 3 -> 4 (head of `B4`): placement 46 -> BFS 43 / 44. **TRAP:** the bookmark `L3skipu_end_r` is not the state the route has
  there (3 bytes differ: pad bytes `$29/$2B` and `$565`, from the Up+Down frame that was removed from L3skipu); a head found from the
  bookmark merges from the bookmark and NOT in the route (`logs/fix/u17c_chain_up17a3.txt`: Level 4 rolls other dice, the end
  differs). From the true state (`C3s_end0b` = `L3u_bikes` + L3skipu) the six 44-frame heads come out one CPU cycle off (ts 0, the
  reference 15); no Select in L3skipu's last 90 frames (84 variants) and no press on the first 8 frames after the placement (288
  variants) moves it. **Not done: -2 open at this page** (`pbeam_C4.json` is the bookmark-only head: DO NOT use it in a route).

## 7. Climb: one gate looked at, nothing found

- `u17c_trace.py` (`logs/fix/u17c_trace_C4.tsv`): per-frame table of the C4 climb. The 150 frames between 3,200 and 3,330 px are a
  clock gate: the floor hole 0x4a at H 3,328 runs between x 59 and 200 at 2 px a frame (period about 141 frames); the toad stands
  on the 3,264 floor from frame 2217 (left of the lift shaft at x 144) and goes through when the hole comes back over x 100-110 at
  2285-2300. `u17c_climb.py` (copy of `u16b_climb3.py` under my names, `U17C_STOP`) from `u16b_climb_mark3100_s3.json` at rate 8
  (almost uniform cost), 160 tries: +3,300 px at 2302 again (C4: 2300). From that arrival there is no earlier pass; one would
  have to stand on the 3,264 floor about 70 frames sooner (one hole pass). The 100 px at 2,400-2,500 are not a clock gate: the toad
  crosses two floors sideways under the fliers. No climb search was run beyond this (hours of machine time for a quantum of 70).

## 8. What is left (for the next batch)

- Level 8 fight: 6 frames per step (kill + death 1073 / 1071 / 1067 ...), fresh seeds of `u17c_fight.py` on C4, then
  `u16b_build.py` + `u17c_mk.py` / `u17c_sync.py` + `u16a_chk.py` + assemble. The floor of the fight is about 618 (chain A).
- Level 3 -> 4 page: -2 if the fine alignment can be moved (a press earlier in L3skipu while the toad is in play risks the skip).
- Odd gains (-3) exist at both head pages; an odd shift cannot merge.
- Karnath room 1 (track K's lead, about 20 frames) and the tower's first 5,000 frames (TOWER1: no `logs/fix/tw1_assemble.txt`
  with a RUN TIME / MATCH line existed when this was written; nothing of it is used).
- Anything rebuilt in front of a level load: count frames mod 6 first (section 4).

## 9. Files

Scripts (`u17c_*.py`): `u17c_lib.py`; `u17c_chain.py` (proof: every segment against its own reference, per frame); `u17c_probe1.py` (one
segment from two entries, which bytes differ); `u17c_sync.py` (alignment scan of a tail, `U17C_QUICK`); `u17c_mk.py` (write one variant);
`u17c_poweron.py` (replay-exact bookmark); `u17c_mkbm.py`; `u17c_fight.py`; `u17c_death.py`; `u17c_tail.py` (padded pages);
`u17c_cls.py` (alignment per frame); `u17c_head.py` / `u17c_head2.py` / `u17c_head3.py` (pages at a segment's head); `u17c_trace.py`;
`u17c_climb.py`.
Segments: **in up17a2: `C1b`, `C3u`, `C6`, `C8c`** (+ `L3skipu`, `B4`, `A9r`, `A10r`, `A11r`, `A12r`, `A13r_k0p16`); in up17a: `C8b`; others:
`C8` (fight h, 3,895), `C8b3` (= C8b with another press), `C8f62_raw`, `C8f62r20_raw`, `C8f63_raw`, `C8f62r17_raw` (builds without a merge
press), `C4` (DO NOT USE, section 6). Bookmarks: `C6_end0` (power-on replay), `C6_end0b`, `C8b_end0b`, `C8c_end0b`, `C1b_end0b`,
`C3u_end0b`, `C3s_end0b`, `C4_end0b`. Fights: `logs/fix/u17c_fight_*.json`. Routes: `up17a2` (best), `up17a`, `up17a0`.
