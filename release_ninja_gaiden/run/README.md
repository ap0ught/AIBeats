# run/: the builders' own proof of the final file

| file | what |
|---|---|
| `NG_FINAL_v2.report.json` | `assemble.py --serial` on the final list: two fresh NesHawk replays, RAM and per-frame trace SHA-1 of each (they match), every stage load / control frame, room changes, cutscenes, deaths (none), lag, and the clock (START seen 175, END seen 41,385, 41,210 frames = 11:25.704) |
| `coord_NG_FINAL_v2.verify.txt` | the coordinator's printout of the same check (judge PASS, per-stage control frames) |
| `NG_FINAL_v2_replay_a.log`, `NG_FINAL_v2_replay_b.log` | EmuHawk's console log of the two replays (core, board, ROM hash) |
| `check_inputs.txt`, `check_inputs.json` | `harness/check_inputs.py ../ninja_gaiden_ai_11m25s.inputs.txt --period 5 --hold 2 --release 2 --windows 600:109,1800:246`: PASS |
| `table.md` | the stage-by-stage table against the record, by the same on-screen event |
| `clock_evidence.json` | the project's START evidence (RAM, OAM sprite count and picture around frames 169-180) |
| `clock/f00170.png` ... `f00180.png` | pictures around START: no Ryu on 174, Ryu on 175 |
| `clock/f41380.png` ... `f41389.png` | pictures around END: TIMER-001 up to 41,384, TIMER-000 from 41,385 |

The final list is `NG_FINAL_v2_poweron.inputs.txt` in the project, released as `../ninja_gaiden_ai_11m25s.inputs.txt`
(same bytes, SHA-1 `cf703880841028f3c77383dcb3345db7cec23884`). The clock pictures come from the independent
checker's replay (`verification/independent_check/final/`).
