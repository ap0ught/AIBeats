# chain2 snapshot - what code this folder runs

Taken 2026-10-16 18:35 (local) from `` by `cp -rp` (root files, `contra/`, `tools/`, `knowledge/`, `states/s1/`, the stage 1 openings and rule v2 lists in `logs/s1/`); this table written 2026-10-16 23:23:33. "against the live folder" compares with the live file at the time this table was written. Fixes made for the chain are in `FIXES.md`; a changed file keeps the snapshot's original next to it as `<name>.snap0`.

Every `contra/stages/*.py` that the chain runs compiled and imported in the snapshot (s1..s8, s7b, s6run, base_room3, base_fight3, base_plan3, base_eye, s3s8_fight, s5_ufo_sim).

| file | bytes | sha1 | mtime | against the live folder | note |
|---|---|---|---|---|---|
| `Contra (USA).nes` | 131088 | `c9ea66bb7cb30ad5343f1721b1d4d3219859319b` | 06-20 17:55:24 | same as live now |  |
| `bridge.lua` | 9916 | `741fd28be18725c6bc5d7c075e8bc0d42a874221` | 10-11 16:51:49 | same as live now |  |
| `assemble.py` | 9557 | `ba332712fec1159ea512c8474b254b357e524c72` | 10-11 16:03:37 | same as live now |  |
| `check_inputs.py` | 7462 | `9e2d577e04e027f0f4f7b4658e53af03e68e6dde` | 10-12 08:26:45 | same as live now |  |
| `contra/__init__.py` | 0 | `da39a3ee5e6b4b0d3255bfef95601890afd80709` | 10-11 15:39:51 | same as live now |  |
| `contra/clock.py` | 5089 | `a39bf4b02af2a9c8e12068b392ebad272dfbc043` | 10-11 16:02:53 | same as live now |  |
| `contra/emulator.py` | 18067 | `c404585bac2a0df4b23bcfca76c8b312d81bf2af` | 10-16 18:35:26 | DIFFERS from live now | PATCHED: `BIZHAWK_DIR` is an explicit path (PROJECT resolves to chain2, so ROM, bridge.lua, states/, logs/, shots/, knowledge/, emu_tmp/ are all chain2's own); original = `emulator.py.snap0` |
| `contra/inputs.py` | 2451 | `9a6420279149639540e80e8b347833171a148c49` | 10-11 15:39:50 | same as live now |  |
| `contra/ramscan.py` | 3700 | `9ceca4a4f3f60d317a5d19c661eaebf35a7e584c` | 10-11 15:49:20 | same as live now |  |
| `contra/resync.py` | 22004 | `374343bcc3facc31abaa0639a2195a2fbe6978e0` | 10-11 17:27:23 | same as live now |  |
| `contra/stages/__init__.py` | 0 | `da39a3ee5e6b4b0d3255bfef95601890afd80709` | 10-11 18:05:37 | same as live now |  |
| `contra/stages/base_bfight.py` | 34605 | `97a6cd0aee68f16b38d56b7e1ab660176bdec304` | 10-12 10:48:13 | same as live now |  |
| `contra/stages/base_boss.py` | 7707 | `02ff143bf419ac38fabfad081a6a93ebd1577594` | 10-11 20:15:50 | same as live now |  |
| `contra/stages/base_boss4.py` | 9459 | `593ed0a285cadc572f6063c6c23e31b0221700bc` | 10-11 21:50:34 | same as live now |  |
| `contra/stages/base_bplan.py` | 17510 | `967f60103498e12bfbdc0c7c4d659156a76248d3` | 10-12 09:29:11 | same as live now |  |
| `contra/stages/base_bsim.py` | 24874 | `289a790d060674815531243fd95e5b5e77b7ea74` | 10-12 03:00:12 | same as live now |  |
| `contra/stages/base_common.py` | 10276 | `3cb1e73449436b789f08453c3cde80f3003e7796` | 10-11 20:49:19 | same as live now |  |
| `contra/stages/base_eye.py` | 9379 | `a323cb7d9fbc50abdbe0efae8c67c7a18b2afc99` | 10-12 10:36:23 | same as live now |  |
| `contra/stages/base_fight3.py` | 16984 | `68b3e7821482c8cfa15444845dd7e83410516484` | 10-16 16:21:12 | same as live now |  |
| `contra/stages/base_plan.py` | 14435 | `0f8443d37b4feaf01372f225f53a195123c615ce` | 10-11 23:04:00 | same as live now |  |
| `contra/stages/base_plan3.py` | 21490 | `e433e762837434c2959d93dd2aee0716f49885cb` | 10-12 09:20:24 | same as live now |  |
| `contra/stages/base_room.py` | 20284 | `aae3fbe36217fbf2b1af36670e9b5f79c3f8b994` | 10-11 23:10:45 | same as live now |  |
| `contra/stages/base_room3.py` | 26722 | `24ddd05dddaa586efee1f80df41a9aa1a9eab97d` | 10-16 16:52:56 | same as live now |  |
| `contra/stages/s1.py` | 43078 | `5951088f85fa4c22812d389d76cc531e6e0683f2` | 10-12 09:36:02 | same as live now |  |
| `contra/stages/s1_common.py` | 20416 | `49c1c1b00097c8abe39888c18d2d8987fcac99d0` | 10-12 08:31:32 | same as live now |  |
| `contra/stages/s1_engine.py` | 30104 | `0523774aa031ce195130b32492853785d4bfe470` | 10-12 09:04:55 | same as live now |  |
| `contra/stages/s2.py` | 9144 | `cca080b4318169d0211b80b8268b2ee741dbe7f0` | 10-12 11:37:13 | same as live now |  |
| `contra/stages/s3.py` | 9669 | `1f7808ba1978d5d7fe7c2de5429f060d423367bb` | 10-12 08:35:54 | same as live now |  |
| `contra/stages/s3_boss.py` | 18296 | `e19df388e8c926d7f8fb46d9b50c2ef1c9259e50` | 10-12 03:04:48 | same as live now |  |
| `contra/stages/s3_climb.py` | 23566 | `10996fb8ced82b92d9a2ef88eecb9cc8a8a02728` | 10-12 01:58:39 | same as live now |  |
| `contra/stages/s3_exec.py` | 7456 | `fc61c5c94687c0cc29b2ce9f3f9b9294a8d49fca` | 10-11 18:54:23 | same as live now |  |
| `contra/stages/s3_model.py` | 5947 | `1d79c8bfa02a53f092dda6c134b0981f6679baef` | 10-11 18:33:49 | same as live now |  |
| `contra/stages/s3_plan.py` | 20964 | `d8d1c3b16d016d7c2bdd90221149229e8e3eb971` | 10-11 19:10:02 | same as live now |  |
| `contra/stages/s3s8_engine.py` | 9104 | `960010a4bdf57c06e1c719d03aae665116c51e04` | 10-12 08:32:36 | same as live now |  |
| `contra/stages/s3s8_fight.py` | 22112 | `c604399c230bb4f199330537f1b14417482ed323` | 10-12 12:02:15 | same as live now |  |
| `contra/stages/s3s8_lib.py` | 18248 | `b242ad8cdf58810b20b53c9f9a5b5834f78b8761` | 10-12 08:35:54 | same as live now |  |
| `contra/stages/s4.py` | 1043 | `5167d7349db310f9dcd5423f76f13dbb0b4d63cf` | 10-12 09:21:05 | same as live now |  |
| `contra/stages/s5.py` | 60605 | `b5cdcdac0af1330807f445a5c4a415f6a97792f5` | 10-12 10:06:35 | same as live now |  |
| `contra/stages/s5_ufo_sim.py` | 11242 | `24963dff29db551bce0df2cbdfc8855455877263` | 10-12 01:19:36 | same as live now |  |
| `contra/stages/s6.py` | 16921 | `fc9691cbb6a7ac45f2f3489a271707f848a7c586` | 10-11 22:54:39 | same as live now |  |
| `contra/stages/s6ctl.py` | 6345 | `1c555c5623f28ce94462ac1f9f685999ae438100` | 10-11 22:39:04 | same as live now |  |
| `contra/stages/s6lib.py` | 9426 | `55793a92cd75ed18fdd6a79689aa8574000b8a97` | 10-11 18:09:40 | same as live now |  |
| `contra/stages/s6run.py` | 48355 | `23bf8ab408a2ed32af06d5c42c9dfe950ce4bb7a` | 10-12 07:43:27 | same as live now |  |
| `contra/stages/s7.py` | 16842 | `1d478b507ff123a7c162094f4153e94408e99897` | 10-12 06:38:25 | same as live now |  |
| `contra/stages/s7b.py` | 37435 | `afd8c987e037342a78ec4a489bc36ecfe7bc5438` | 10-12 07:10:53 | same as live now |  |
| `contra/stages/s7lab.py` | 1462 | `3496e7de2e0f06c98c5c5c63eec4c27e46d11e07` | 10-12 02:30:17 | same as live now |  |
| `contra/stages/s8.py` | 56596 | `ac60295a6c74d4c8bc604fa8e140f4d430942d6c` | 10-16 15:42:39 | same as live now |  |
| `tools/s2_solve.py` | 3067 | `7145e73cbcbcc9749d8708659b032b0454048d72` | 10-12 09:21:05 | same as live now |  |
| `tools/s6_solve.py` | 3430 | `dfdff96791547239d4384c6ce3a0ff3478926ccb` | 10-11 19:12:19 | same as live now |  |
| `tools/s1_open.py` | 3522 | `2c5f657710fb4afd7bc466a2a5864c45fb39b1ad` | 10-11 21:59:28 | same as live now |  |
| `tools/s1_finish.py` | 4979 | `878d5356d64a7b34ea1ad5c5d36606d104f9d5fe` | 10-11 21:59:28 | same as live now |  |
| `tools/s5_finish.py` | 4568 | `eae35564314b9274ceb1d967d28baa10c1de38c6` | 10-11 20:01:14 | same as live now |  |
| `tools/s2_verify.py` | 4707 | `a8839fde472908df69fd2a018b33900faf5a131c` | 10-12 02:31:09 | same as live now |  |
| `knowledge/ram.json` | 10435 | `b893b806c6211b314984a3282e6350cf08637b58` | 10-11 17:41:59 | same as live now |  |
| `knowledge/record_events.json` | 17463 | `6080fb4e9292c33c1f2f30f76c1ebd6b29fb5816` | 10-11 16:47:58 | same as live now |  |
| `knowledge/record_mash_rate.json` | 15152 | `2ac7b6c73a95b02363f55575c1309c660954ce5e` | 10-12 08:20:42 | same as live now |  |
| `knowledge/s3_map.json` | 9016 | `169bcc768bdb3643c5c281eb81675fe8baafe361` | 10-11 18:38:46 | same as live now |  |
| `knowledge/s6_map.json` | 18095 | `1e592266f5ceaa9f3f473149a6a5209112db3b75` | 10-11 18:10:05 | same as live now |  |
| `knowledge/s6_phase_table.json` | 55521 | `26841f8b77d2b105f75a045197ef7d274b585ef2` | 10-12 02:06:30 | same as live now |  |
| `knowledge/s7_map.json` | 24933 | `93522753354f8621b173edd2f95bb29623f6abb8` | 10-11 18:10:35 | same as live now |  |
| `knowledge/s7_phase_table.json` | 80661 | `21eeb636aebe3dd7cc2a9601d1be9425a340d10c` | 10-12 08:25:05 | same as live now |  |
| `knowledge/s7_record_landmarks.json` | 29095 | `823d371a0d94ca11419e8059acf2fbd1aa240cad` | 10-12 08:24:53 | same as live now |  |
| `knowledge/s8_map.json` | 9428 | `e1cd87b9ca0047d1905f2222590d029c609358c0` | 10-11 18:12:58 | same as live now |  |
| `knowledge/tas_compare.json` | 9691 | `88d3bce26c93c082e14f01cfb6ce5e55717a68aa` | 10-16 18:34:10 | same as live now |  |
| `logs/s1/s1_w0v3_full.inputs.txt` | 26289 | `07e4f9d9462622db841c5989e2e28d170e7a5684` | 10-12 09:46:31 | same as live now | stage 1, title_wait 0, rule v2 (verified list; chain A's stage 1) |
| `logs/s1/s1_w1v3_full.inputs.txt` | 26223 | `0bb6f35ec068196c8226920d1c3cea7afd940cc2` | 10-12 10:43:15 | same as live now |  |
| `logs/s1/s1_w37v3_full.inputs.txt` | 26364 | `4a483571e9bbb969ba571946d1b47d4f6c317f15` | 10-12 11:08:31 | same as live now |  |
| `states/s1/s2_start_legal_v3.State` | 19064 | `b0d71b5558290e9e26a401a6d54433d4a9388dd8` | 10-12 09:49:32 | same as live now | stage 2's first frame of the w0v3 list (the chain makes its own from a replay) |

chain2's own files: `chain.py` (from chain1's, see its docstring), `run_s67.py` (chain1's, history tail 2,000 rows), `finish.py`, `clock_shots.py`, `snapshot_table.py`.
