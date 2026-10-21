"""Independent analysis of the two replays (runA, runB). RAM addresses are from the third-party disassembly
(vermiceli/nes-contra-us, src/ram.asm), not from the builders' files. Writes vanalyze.out.json."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REC = 2310


def load(run):
    b = (HERE / run / "trace.bin").read_bytes()
    assert len(b) % REC == 0
    n = len(b) // REC
    return b, n


def rec(b, k):
    """k = emulator frame number (first record is frame 2)."""
    o = (k - 2) * REC
    r = b[o:o + REC]
    f = r[0] | r[1] << 8 | r[2] << 16
    assert f == k, (f, k)
    return {"lag": r[4], "mask": r[5], "ram": r[6:6 + 2048], "oam": r[6 + 2048:]}


A, nA = load("runA")
B, nB = load("runB")
out = {}
out["records"] = [nA, nB]
out["trace_sha1"] = [hashlib.sha1(A).hexdigest(), hashlib.sha1(B).hexdigest()]
out["trace_identical"] = A == B
last_in = 34568                       # 34567 rows, first applied on frame 2
last = nA + 1
for k in (594, 5000, 10000, 20000, 30000, last_in, last):
    ra, rb = rec(A, k), rec(B, k)
    out[f"ram_sha1_f{k}"] = [hashlib.sha1(ra["ram"]).hexdigest(), hashlib.sha1(rb["ram"]).hexdigest()]

# pictures: every frame, file bytes
mism, missing, cnt = [], [], 0
h_all_a, h_all_b = hashlib.sha1(), hashlib.sha1()
checkpoints = {}
for k in range(2, last + 1):
    pa, pb = HERE / "runA" / f"f{k:05d}.png", HERE / "runB" / f"f{k:05d}.png"
    if not pa.exists() or not pb.exists():
        missing.append(k)
        continue
    da, db = pa.read_bytes(), pb.read_bytes()
    ha, hb = hashlib.sha1(da).digest(), hashlib.sha1(db).digest()
    h_all_a.update(ha)
    h_all_b.update(hb)
    cnt += 1
    if ha != hb:
        mism.append(k)
    if k % 2500 == 0 or k in (last_in, last):
        checkpoints[k] = [ha.hex(), hb.hex()]
out["pictures_compared"] = cnt
out["pictures_missing"] = missing[:20]
out["pictures_mismatching"] = mism[:20]
out["pictures_mismatch_count"] = len(mism)
out["pictures_chain_sha1"] = [h_all_a.hexdigest(), h_all_b.hexdigest()]
out["picture_checkpoints_sha1"] = checkpoints

# RAM timeline from run A
WATCH = {"game_routine_18": 0x18, "demo_1c": 0x1C, "player_mode_22": 0x22, "konami_24": 0x24, "pause_25": 0x25,
         "level_routine_2c": 0x2C, "end_level_routine_2d": 0x2D, "level_30": 0x30, "completion_31": 0x31,
         "p1_lives_32": 0x32, "p2_lives_33": 0x33, "p1_gameover_38": 0x38, "continues_3a": 0x3A,
         "boss_defeated_3b": 0x3B, "p1_weapon_aa": 0xAA, "death_flag_b4": 0xB4, "player_state_90": 0x90,
         "p2_state_91": 0x91, "game_end_routine_19": 0x19}
prev = {}
events = {k: [] for k in WATCH}
p2_nonzero = 0
p2_diff_nonzero = 0
pad_mismatch = []
lag_frames = []
for k in range(2, last + 1):
    r = rec(A, k)
    ram = r["ram"]
    for name, a in WATCH.items():
        v = ram[a]
        if prev.get(name) != v:
            events[name].append([k, v])
            prev[name] = v
    if ram[0xF2] or ram[0xFA]:
        p2_nonzero += 1
    if ram[0xF6]:
        p2_diff_nonzero += 1
    if r["lag"]:
        lag_frames.append(k)
    elif ram[0xF1] != r["mask"]:
        pad_mismatch.append(k)
for name in WATCH:
    ev = events[name]
    out["tl_" + name] = ev if len(ev) <= 80 else {"changes": len(ev), "first": ev[:30], "last": ev[-30:]}
out["p2_controller_nonzero_frames"] = p2_nonzero
out["p2_controller_diff_nonzero_frames"] = p2_diff_nonzero
out["lag_frames_total"] = len(lag_frames)
out["nonlag_frames_where_game_pad_byte_differs_from_sent"] = {"count": len(pad_mismatch), "first": pad_mismatch[:40]}
out["lives_values_seen"] = sorted({rec(A, k)["ram"][0x32] for k in range(2, last + 1)})
out["weapon_values_seen"] = sorted({rec(A, k)["ram"][0xAA] for k in range(2, last + 1)})
(HERE / "vanalyze.out.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
(HERE / "lag_frames.json").write_text(json.dumps(lag_frames), encoding="utf-8")
for k, v in out.items():
    s = json.dumps(v)
    print(k, "=", s if len(s) < 1500 else s[:1500] + " ...")
