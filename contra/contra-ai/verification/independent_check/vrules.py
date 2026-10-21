"""Rule / sanity findings from the replay's RAM trace (runA) and pictures. Addresses from the third-party
disassembly (vermiceli/nes-contra-us src/ram.asm). Writes vrules.out.json."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REC = 2310
T = (HERE / "runA" / "trace.bin").read_bytes()
N = len(T) // REC
LAST = N + 1
START, END = 594, 34509           # from vclock.py (pictures)


def ram(k):
    o = (k - 2) * REC + 6
    return T[o:o + 2048]


def lag(k):
    return T[(k - 2) * REC + 4]


def mask(k):
    return T[(k - 2) * REC + 5]


out = {}
# stage table
stages = []
cur = None
for k in range(3, LAST + 1):
    r, p = ram(k), ram(k - 1)
    if r[0x2C] == 4 and p[0x2C] != 4 and r[0x1C] == 0:
        cur = {"level_30": r[0x30], "play_from_ram_frame": k, "lives_at_start": r[0x32], "weapon_at_start": r[0xAA]}
        stages.append(cur)
    if cur is not None and r[0x3B] == 1 and p[0x3B] == 0:
        cur["boss_defeated_ram_frame"] = k
    if cur is not None and r[0x2C] == 9 and p[0x2C] == 8:
        cur["control_lost_ram_frame"] = k
for i, s in enumerate(stages):
    a = s["play_from_ram_frame"]
    b = s.get("control_lost_ram_frame", LAST)
    s["frames_play_to_control_lost"] = b - a
    s["lag_frames_in_play"] = sum(lag(k) for k in range(a, b + 1))
    scr = []
    for k in range(a, b + 1):
        v = ram(k)[0x64]
        if not scr or scr[-1][1] != v:
            scr.append((k, v))
    s["screen_number_64_sequence"] = [v for _, v in scr]
    s["screen_steps_all_plus1"] = all(scr[j + 1][1] - scr[j][1] == 1 for j in range(len(scr) - 1))
    ys = [ram(k)[0x31A] for k in range(a, b + 1)]
    xs = [ram(k)[0x334] for k in range(a, b + 1)]
    s["p1_y_range"] = [min(ys), max(ys)]
    s["p1_x_range"] = [min(xs), max(xs)]
    s["player_state_values"] = sorted({ram(k)[0x90] for k in range(a, b + 1)})
    s["frames_player_hidden_ba"] = sum(1 for k in range(a, b + 1) if ram(k)[0xBA])
    s["jump_coefficient_94_max"] = max(ram(k)[0x94] for k in range(a, b + 1))
    s["seconds_from_START_to_boss_defeated"] = round((s.get("boss_defeated_ram_frame", 0) + 1 - START) / 60.0988, 3)
out["stages"] = stages
out["stages_played"] = [s["level_30"] for s in stages]

# timed span
span = range(START, END + 1)
out["lag_frames_in_timed_span(START..END-1)"] = sum(lag(k) for k in range(START, END))
out["lag_frames_total_trace"] = sum(lag(k) for k in range(2, LAST + 1))
# pad byte the game saw vs what was sent, during play (routine 4, not paused, not lag)
ign = []
for k in range(START, END + 1):
    r = ram(k)
    if lag(k) or r[0x2C] != 4:
        continue
    if r[0xF1] != mask(k):
        ign.append((k, mask(k), r[0xF1]))
out["play_frames_where_game_pad_byte_differs"] = {"count": len(ign), "first": ign[:25]}
# of those, how many are "previous frame's buttons reused" (the DMC read conflict signature)
reuse = sum(1 for k, m, f in ign if f == ram(k - 1)[0xF1])
out["...of_which_equal_previous_frame_pad_byte"] = reuse
# pauses
pz = []
k = START
while k <= END:
    if ram(k)[0x25] == 1:
        a = k
        while ram(k)[0x25] == 1:
            k += 1
        pz.append({"paused_ram_frames": [a, k - 1], "length": k - a, "level_30": ram(a)[0x30],
                   "rng_34_before_after": [ram(a - 1)[0x34], ram(k)[0x34]],
                   "frame_counter_1a_before_after": [ram(a - 1)[0x1A], ram(k)[0x1A]]})
    k += 1
out["pauses"] = pz
out["total_paused_frames"] = sum(p["length"] for p in pz)
# lives / deaths / mode / konami across the timed span
out["p1_lives_32_sequence"] = []
prev = None
for k in range(2, LAST + 1):
    v = ram(k)[0x32]
    if v != prev:
        out["p1_lives_32_sequence"].append([k, v])
        prev = v
out["lives_ever_decrease_in_span"] = any(ram(k)[0x32] < ram(k - 1)[0x32] for k in range(START, END + 1))
out["death_flag_b4_ever_set_in_span"] = any(ram(k)[0xB4] & 1 for k in range(START, END + 1))
out["player_state_2_dead_ever_in_span"] = any(ram(k)[0x90] == 2 for k in range(START, END + 1))
out["player_mode_22_values"] = sorted({ram(k)[0x22] for k in range(3, LAST + 1)})
out["konami_24_values_after_frame2"] = sorted({ram(k)[0x24] for k in range(3, LAST + 1)})
out["konami_progress_3f_max_before_start"] = max(ram(k)[0x3F] for k in range(3, 340))
out["p2_state_91_values"] = sorted({ram(k)[0x91] for k in range(3, LAST + 1)})
out["p2_pad_f2_nonzero_frames"] = [k for k in range(2, LAST + 1) if ram(k)[0xF2]][:10]
out["p2_pad_diff_f6_nonzero_frames"] = [k for k in range(2, LAST + 1) if ram(k)[0xF6]][:10]
out["continues_3a_values_in_span"] = sorted({ram(k)[0x3A] for k in range(START, END + 1)})
out["game_over_38_values"] = sorted({ram(k)[0x38] for k in range(3, LAST + 1)})
out["weapon_aa_sequence"] = []
prev = None
for k in range(2, LAST + 1):
    v = ram(k)[0xAA]
    if v != prev:
        out["weapon_aa_sequence"].append([k, v])
        prev = v
# invincibility (B item) and other pickups
out["barrier_timer_b0_nonzero_frames"] = sum(1 for k in range(START, END + 1) if ram(k)[0xB0])
out["new_life_invincibility_ae_nonzero_frames_after_first_300"] = sum(1 for k in range(START + 300, END + 1) if ram(k)[0xAE])

# pictures: P2 medals never shown (top right HUD), P1 medal count through the run (every 30th frame of play)
blue = np.array([66, 64, 254])


def hud_blue(f, x0, x1):
    a = np.asarray(Image.open(HERE / "runA" / f"f{f:05d}.png").convert("RGB")).astype(np.int16)[8:26, x0:x1]
    return int((np.abs(a - blue).sum(axis=2) == 0).sum())


p2_hits = 0
medal_counts = {}
for s in stages:
    a, b = s["play_from_ram_frame"] + 2, s.get("control_lost_ram_frame", LAST)
    seen = set()
    for f in range(a, b, 30):
        if hud_blue(f, 200, 256) >= 20:
            p2_hits += 1
        n1 = hud_blue(f, 8, 64)
        seen.add(round(n1 / 35))
    medal_counts[s["level_30"]] = sorted(seen)
out["picture_frames_with_p2_hud_medals(sampled)"] = p2_hits
out["picture_p1_medals_shown_per_stage(sampled, HUD shows at most 4)"] = medal_counts
(HERE / "vrules.out.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for k, v in out.items():
    if k == "stages":
        for s in v:
            print(json.dumps(s))
    else:
        print(k, "=", json.dumps(v))
