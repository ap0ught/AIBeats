* **l62 STATUS / RESUME (2026-10-28 ~07:25; all my emulators stopped).** Built and NesHawk-verified from power-on to the room-40 platform
  approach; the room-40 run to the 6-2 -> 6-3 trigger is NOT finished.
  * **Verified chain:** `work/l62/l62_po_r40f.inputs.txt` (34,924 rows; judge PASS): 5-4 Start 30,903-04, **6-1 control 31,057**, 6-2 control
    32,632 (F + 1,575 = TAS), room 37 33,567 (TAS + 994 = +0), **room 38 34,261 (+97)**, **room 39 34,375 (+113)**, **room 40 34,877 (+171 vs TAS
    33,712; the record's room-40 change is TAS +207.0 -> we are ~-36 vs the record there)**, hp 15, np 0, J&S. NesHawk = Mesen (0 RAM diffs at
    33,589 / 34,397 / 34,924). NesHawk states: `l62_k30306`, `l62_31056`, `l62_32631`, `l62_33567`, `l62_33589`, `l62e_34260`, `l62e_34397`,
    `l62f_34900` (room-40 control - 1). Mesen: `states/mesen/l62_33589.mst` (room 37), `states/mesen/l62e_34397.mst` (room-39 control - 1).
  * **Room 40 so far (Mesen only):** `work/l62/b_r40g.txt` (rows from 33,590: entry cycle x4 + staircase beam) -> on the y-96 platform
    (X >= 112) on 35,046; then beam `r40l` checkpoint **`work/l62/r40l_ckpt_35357.txt`** (rows from 33,590 to 35,357: X 578 y 208 on the
    floor, hp 14, np 0; the run along the top and down to the floor at pure 1.5 px/f, ~TAS + 27 from the platform; one 1-hp hit).
  * **Open problem = the pit X ~624-703 on the y-208 floor before the exit floor (X 704-751; trigger at X 747 y 208).** The TAS crosses it with a
    jump at X 609 (34,185) and a damage boost (hp 14 -> 12 on 34,200, enemy near X 630 y 160) up to y 128, then right to X 709 y 156. My
    X-scored beams fall in (`r40i`: best X 694 y 205, then all nodes die); a height-penalty score made a false wall at X 590 (`r40m`). Not
    tested yet: a beam from the 35,357 checkpoint (or from ~35,300) with goal `X >= 704 and y <= 208 and rm == 40` (land on the far floor),
    hits allowed (`--minhp 2`), score `X - 0.5*y`, alphabet incl. A+Right / B+Right / A. Then `python work/l62/fin.py <rows> <stage out>
    <poweron out>` (finds the trigger = `$5C` 2 -> 0 in room 40, holds Right to trigger + 279 = 6-3 control, writes the power-on file), judge,
    and `python work/l62/nhrun.py <poweron> l62f_34900 34901 <end> 0` for the NesHawk check.
  * **Expected finish:** if the pit costs ~the TAS's line, trigger ~35,47x-35,49x -> 6-3 control ~35,75x-35,77x = 6-2 control + ~3,120-3,140
    vs the record's 3,153 (about -15..-35). 6-3 control `$BF` = (row - 27) mod 256: the good runs 113-122 / 223-255 are rows 35,724-35,733 and
    35,578-35,610 / 35,834-35,866; report the real one after `fin.py`.
  * Ninpo: np 0 from room 39's exit on (coordinator's new target J&S + 0..4 at the 6-3 control is met so far; skip the room-40 +5 X 304 /
    +10 X 512 or burn them with air spins). J&S held throughout.
  * Tools: `work/l62/b62.py` (beam; `--mst`, `--poke`, `--minnp`, checkpoint file `b_<tag>_ckpt.txt` every `--dbg` frames, Mesen RAM floor
    lowered to 1.2 GB for low-RAM mode), `ch62.py` (rooms 37-40 chain), `mk40.py`, `fin.py`, `nhrun.py`, `mkm.py`, `tr.py`, `mkpo.py`/`mkpo2.py`.
