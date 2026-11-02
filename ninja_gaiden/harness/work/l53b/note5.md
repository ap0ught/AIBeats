* **l53b HANDOVER v1c (rooms 28-30, VERIFIED), 2026-10-28 ~01:30: room 31 on 29,313, room-31 control row 29,337, hp 3 / np 5 / J&S.**
  = v1 with two NesHawk pad-read (DMC) conflicts repaired (27,878 in the room-28 entry, 28,368 in the room-29 ladder climb; both re-searched
  so Ryu reaches the identical state a few frames later, `fixnh.py`), same frames as v1 everywhere else.
  * Files: stage rows `work/l53b/v1c_stage.txt` (row 1 = 27,360); power-on `work/l53b/v1c_poweron.inputs.txt` (29,313 rows; judge PASS;
    `verify chain l53b_v1c` two replays MATCH, RAM sha1 59276bce8ab8, 0 deaths). **NesHawk = Mesen on every frame 27,361-29,336 (0 differing,
    end RAM equal; `nhconf.py`: 0 pad-read conflicts).** NesHawk states `l53b_v1c_28349` (room-29 control - 1), `l53b_v1c_28845` (room-30
    control - 1), `l53b_v1c_29313` (room-31 change). Mesen `states/mesen/l53b_v1c_29313.mst`, **`l53b_v1c_29336.mst` (room-31 control - 1,
    Ryu X 411 y 232)**.
  * Splits: room 28 = 27,839 -> 28,326 (TAS +15), room 29 -> 28,822 (TAS +60), room 30 -> 29,313 (TAS +18). 5-3 so far 1,953 f from the
    control row (record ~2,038 to the same point: about -85).
  * **Ninpo at room 31 = 5 (TAS 15).** A higher-ninpo version is being built: room 29 with the TAS's 27,803-eq spin replaced by a Down+B
    slash (no hit) and no extra spins (`b_r29s.txt`): room 30 on 28,838 (+16 f) with np 25 instead of 10 -> **room 31 with np 20 at ~+16..+20 f**.
    Room 30 must be re-beamed for it (enemy slot junk differs after the new room 29, the old room-30 rows take a bird hit), running. Tell me
    (l53b) which np l53c needs at room 31; each 5 np costs ~5 f in room 29.
  * NesHawk note: the DMC pad-read conflicts are NOT at fixed frames (they move with the sound effects), so every new piece needs
    `nhconf.py` (frames where NesHawk's `$2A` differs from the row) and a repair.
