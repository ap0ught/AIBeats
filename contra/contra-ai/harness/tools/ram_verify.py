"""Check RAM-map claims against a full-RAM capture (tools/ram_capture.py) of a run from power-on.

    python tools/ram_verify.py <capture name>        reads logs/<name>.ram.npy / .oam.npy / .meta.npy / .ram_inputs.txt

Every check is a statement about what was OBSERVED in this capture; the output (also logs/<name>.ramverify.json)
is what knowledge/ram_notes.md quotes. Nothing here reads the disassembly.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import LOGS_DIR  # noqa: E402
from contra.inputs import to_mask  # noqa: E402

name = sys.argv[1]
ram = np.load(LOGS_DIR / f"{name}.ram.npy").astype(np.int32)
oam = np.load(LOGS_DIR / f"{name}.oam.npy").astype(np.int32)
meta = np.load(LOGS_DIR / f"{name}.meta.npy")
inputs = (LOGS_DIR / f"{name}.ram_inputs.txt").read_text(encoding="utf-8").split("\n")
n = len(ram)
frame, lagc, lagged = meta[:, 0], meta[:, 1], meta[:, 2]
mask = np.array([to_mask([b for b in s.split("+") if b]) for s in inputs[:n]] + [0] * (n - len(inputs)))
out = {"capture": name, "rows": int(n - 1), "first_frame": int(frame[0]), "last_frame": int(frame[-1])}


def runs(a):
    """[(value, first frame)] for every change of a byte."""
    r = [(int(a[0]), int(frame[0]))]
    for i in range(1, n):
        if a[i] != a[i - 1]:
            r.append((int(a[i]), int(frame[i])))
    return r


def R(addr):
    return ram[:, addr]


play = (R(0x18) == 5) & (R(0x2C) == 4) & (R(0x1C) == 0)
out["$18 game routine"] = runs(R(0x18))[:20]
out["$2C level routine"] = runs(R(0x2C))[:30]
out["$30 level"] = runs(R(0x30))
out["$6A hud flag"] = runs(R(0x6A))[:10]
out["$1C demo"] = runs(R(0x1C))[:6]
out["$22 player mode"] = runs(R(0x22))[:6]
out["$24 konami"] = runs(R(0x24))[:6]

# frame counter and lag
dfc = (R(0x1A)[1:] - R(0x1A)[:-1]) % 256
lg = lagged[1:]
out["$1A frame counter"] = {
    "non-lag frames": int((lg == 0).sum()), "of which counter +1": int(((lg == 0) & (dfc == 1)).sum()),
    "non-lag frames with another step (frame, step)": [(int(frame[i + 1]), int(dfc[i])) for i in np.nonzero((lg == 0) & (dfc != 1))[0][:12]],
    "lag frames": int((lg == 1).sum()), "of which counter unchanged": int(((lg == 1) & (dfc == 0)).sum()),
    "lag frames where it changed (frame, step)": [(int(frame[i + 1]), int(dfc[i])) for i in np.nonzero((lg == 1) & (dfc != 0))[0][:12]],
    "lag frames (first 60)": [int(frame[i + 1]) for i in np.nonzero(lg == 1)[0][:60]],
}
out["$1B nmi check at frame end"] = {str(k): int(v) for k, v in zip(*np.unique(R(0x1B), return_counts=True))}
out["$34 rng"] = {"frames on which it changed": int((R(0x34)[1:] != R(0x34)[:-1]).sum()), "of": int(n - 1),
                  "distinct values": int(len(np.unique(R(0x34))))}
# controller byte vs what was sent
pm = play & (lagged == 0) & (R(0x25) == 0)
mis = np.nonzero(pm & (R(0xF1) != mask))[0]
out["$F1 controller byte"] = {"play frames compared": int(pm.sum()), "frames where it differs from the input sent": int(len(mis)),
                              "first (frame, sent, seen)": [(int(frame[i]), int(mask[i]), int(R(0xF1)[i])) for i in mis[:15]],
                              "of those, equal to the PREVIOUS frame's byte": int(sum(1 for i in mis if R(0xF1)[i] == R(0xF1)[i - 1]))}
# position: x moves +1 per frame while Right is seen and the screen does not scroll; scroll +1 while x == 128
x, y, scr, off = R(0x334), R(0x31A), R(0x64), R(0x65)
world = scr * 256 + off
idx = np.nonzero(play[1:] & play[:-1] & (lagged[1:] == 0))[0] + 1
right = (R(0xF1)[idx] & 1) == 1
dx = x[idx] - x[idx - 1]
dw = world[idx] - world[idx - 1]
out["$0334 x / $64:$65 scroll"] = {
    "play frames with Right seen": int(right.sum()),
    "of which x+1 and scroll 0": int((right & (dx == 1) & (dw == 0)).sum()),
    "of which x+0 and scroll +1": int((right & (dx == 0) & (dw == 1)).sum()),
    "of which neither": int((right & ~(((dx == 1) & (dw == 0)) | ((dx == 0) & (dw == 1)))).sum()),
    "x while scrolling (values)": sorted(set(int(v) for v in x[idx][dw == 1]))[:6],
    "max scroll step per frame": int(dw.max()) if len(dw) else None,
    "$65 wraps to 0 exactly when $64 increments": bool(all(off[i] < off[i - 1] for i in range(1, n) if scr[i] == scr[i - 1] + 1 and play[i] and play[i - 1])),
    "$FD equals $65 on play frames (stage 1)": int((R(0xFD)[play & (R(0x30) == 0)] == off[play & (R(0x30) == 0)]).sum()),
    "play frames in stage 1": int((play & (R(0x30) == 0)).sum()),
    "$68 FRAME_SCROLL equals the scroll step": int((R(0x68)[idx] == dw).sum()), "compared": int(len(idx)),
}
# the player sprite: does (x, y) match where the PPU draws him?  (OAM of frame f+1 = sprite list built on frame f)
hits = tot = 0
for i in np.nonzero(play)[0][:-1]:
    if R(0x90)[i] != 1 or R(0xBA)[i] != 0:
        continue
    o = oam[i + 1].reshape(64, 4)
    vis = o[o[:, 0] < 0xEF]
    if len(vis) == 0:
        continue
    tot += 1
    # any sprite tile within the player's box (x-16..x+16, y-34..y+8)
    if ((np.abs(vis[:, 3] - x[i]) <= 16) & (vis[:, 0] - y[i] <= 8) & (vis[:, 0] - y[i] >= -36)).any():
        hits += 1
out["player position vs PPU OAM (next frame)"] = {"play frames checked": tot, "frames with sprite tiles at (x,y)": hits}
out["$90 player state"] = runs(R(0x90))[:12]
out["$AE new-life invincibility"] = runs(R(0xAE))[:6] + ["..."] + [("frames at which it first reads 0 after a stage start",
                                                                  [int(frame[i]) for i in range(1, n) if R(0xAE)[i] == 0 and R(0xAE)[i - 1] == 1][:4])]
out["$B0 barrier timer"] = runs(R(0xB0))[:8]
out["$AA weapon"] = [(hex(v), f) for v, f in runs(R(0xAA))]
out["$32 lives"] = runs(R(0x32))
out["$07E2/$07E3 score at lives changes"] = [(int(frame[i]), int(R(0x7E2)[i] + 256 * R(0x7E3)[i]), int(R(0x3C)[i] + 256 * R(0x3D)[i]))
                                             for i in range(1, n) if R(0x32)[i] != R(0x32)[i - 1]][:6]
out["$B4 death flag"] = runs(R(0xB4))[:8]
out["$3B boss defeated"] = runs(R(0x3B))
out["$2D end-level sub-routine"] = runs(R(0x2D))[:10]
out["$2A delay"] = [r for r in runs(R(0x2A)) if r[0] in (0xFF, 0xC0, 0x80, 0x40)][:12]
# pose
pp = play & (R(0x90) == 1)
for nm, a in (("$BC sprite sequence", 0xBC), ("$C2 aim direction", 0xC2), ("$A0 jump status", 0xA0), ("$D6 sprite code", 0xD6)):
    v, c = np.unique(R(a)[pp], return_counts=True)
    out[nm + " (value: frames)"] = {hex(int(k)): int(cc) for k, cc in zip(v, c)}
g = pp & (R(0xA0) == 0) & (R(0xA4) == 0)
out["pose by input on the ground"] = {
    "Up only -> $BC": sorted(set(int(v) for v in R(0xBC)[g & (R(0xF1) & 0x0F == 0x08)])),
    "Down only -> $BC": sorted(set(int(v) for v in R(0xBC)[g & (R(0xF1) & 0x0F == 0x04)])),
    "Right only -> $BC": sorted(set(int(v) for v in R(0xBC)[g & (R(0xF1) & 0x0F == 0x01)])),
    "nothing -> $BC": sorted(set(int(v) for v in R(0xBC)[g & (R(0xF1) & 0x0F == 0)])),
    "nothing -> $C2": sorted(set(int(v) for v in R(0xC2)[g & (R(0xF1) & 0x0F == 0)])),
    "Up only -> $C2": sorted(set(int(v) for v in R(0xC2)[g & (R(0xF1) & 0x0F == 0x08)])),
    "Up+Right -> $C2": sorted(set(int(v) for v in R(0xC2)[g & (R(0xF1) & 0x0F == 0x09)])),
    "Down+Right -> $C2": sorted(set(int(v) for v in R(0xC2)[g & (R(0xF1) & 0x0F == 0x05)])),
}
# jump: A newly seen on the ground -> $A0 low nibble 1
newA = [i for i in range(1, n) if pp[i] and (R(0xF1)[i] & 0x80) and not (R(0xF1)[i - 1] & 0x80) and R(0xA0)[i - 1] == 0 and R(0xA4)[i - 1] == 0]
out["$A0 after a new A press on the ground"] = {"presses": len(newA), "with $A0 & 15 == 1 that frame or the next": int(sum(1 for i in newA if (R(0xA0)[i] & 15) == 1 or (R(0xA0)[min(i + 1, n - 1)] & 15) == 1))}
# bullets
nb = (ram[:, 0x388:0x398] != 0).sum(axis=1)
newB = [i for i in range(1, n) if pp[i] and (R(0xF5)[i] & 0x40)]
out["player bullets $0388+i"] = {"max live at once": int(nb.max()), "frames with a new B press ($F5 bit 6)": len(newB),
                                 "of which the live-bullet count rose that frame": int(sum(1 for i in newB if nb[i] > nb[i - 1])),
                                 "slots ever used": [int(s) for s in np.nonzero((ram[:, 0x388:0x398] != 0).any(axis=0))[0]]}
# enemies: every slot life with HP > 8 at any time (bosses / tough ones)
tough = []
for s in range(16):
    alive = R(0x4B8 + s) != 0
    i = 0
    while i < n:
        if alive[i]:
            j = i
            while j < n and alive[j] and R(0x528 + s)[j] == R(0x528 + s)[i]:
                j += 1
            hp = R(0x578 + s)[i:j]
            if hp.max() > 8 and R(0x528 + s)[i] != 1:
                drops = [(int(frame[i + k]), int(hp[k])) for k in range(1, j - i) if hp[k] < hp[k - 1]]
                tough.append({"slot": s, "type": hex(int(R(0x528 + s)[i])), "level": int(R(0x30)[i]), "frames": [int(frame[i]), int(frame[j - 1])],
                              "hp max": int(hp.max()), "hp at end": int(hp[-1]), "hp decrements": len(drops),
                              "first drops": drops[:4], "last drops": drops[-3:],
                              "x,y at first drop": [int(R(0x33E + s)[i]), int(R(0x324 + s)[i])]})
            i = j
        else:
            i += 1
out["enemy slots with HP > 8 (type, life, hp)"] = tough[:40]
bd = [i for i in range(1, n) if R(0x3B)[i] == 1 and R(0x3B)[i - 1] == 0]
out["boss defeated flag vs enemy HP"] = [{"frame": int(frame[i]), "level": int(R(0x30)[i]),
                                          "tough slots whose HP reached 0 in the 80 frames before": [t["slot"] for t in tough if t["hp at end"] == 0 and 0 <= frame[i] - t["frames"][1] <= 80 or (t["last drops"] and 0 <= frame[i] - t["last drops"][-1][0] <= 80 and t["last drops"][-1][1] == 0)]} for i in bd]
(LOGS_DIR / f"{name}.ramverify.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
for k, v in out.items():
    print(f"{k}: {json.dumps(v, default=str)[:900]}")
