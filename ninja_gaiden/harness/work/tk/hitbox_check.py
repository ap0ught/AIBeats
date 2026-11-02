"""Cross-check ng.solve.hitbox against the game: replay TAS rows from a ref4751 state, record RAM after every frame,
and compare predicted sword / hurt events with what the game did (enemy hp/slot changes, Ryu knockback $93 bit 7).
    python work/tk/hitbox_check.py <ref state> <first frame> <n frames>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C, hitbox as H
from ng.mode import TICKS
import a56_common as A

st, f0, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rows = A.tas_rows()[f0:f0 + n]
e = C.open_emu("tk_hitbox_check.log")
try:
    e.tick(TICKS)
    e.load(st)
    states, rams = e.run_ram(rows)
finally:
    e.close()
sw_tp = sw_fn = sw_fp = 0
hu_tp = hu_fn = hu_fp = 0
for t in range(1, len(rams)):
    prev, cur = rams[t - 1], rams[t]
    # actual sword hits this frame: an occupied enemy slot whose hp dropped or which started dying, while Ryu's pose was a hit pose
    pose = cur[0x83]
    for en in H.enemies(prev):
        i = en["slot"]
        hit_real = (cur[0x490 + i] < prev[0x490 + i]) or ((cur[0x498 + i] & 0x10) and not (prev[0x498 + i] & 0x10))
        # predicted with Ryu/enemy positions as they are at the start of this frame's enemy turn (approx: cur Ryu, prev enemy)
        ram_mix = bytearray(cur)
        for a in (0x460, 0x480, 0x438):
            ram_mix[a + i] = prev[a + i]
        pred = H.sword_hits(ram_mix, en) or H.sword_hits(cur, dict(en, x=cur[0x460 + i], y=cur[0x480 + i]))
        if pose in (7, 0x0A):
            if hit_real and pred: sw_tp += 1
            elif hit_real and not pred: sw_fn += 1; print("sword FN", f0 + t, i, en["type"], en["x"], en["y"], cur[0x86], cur[0x8A], hex(cur[0x84]))
            elif pred and not hit_real: sw_fp += 1
    kb = (cur[0x93] & 0x80) and not (prev[0x93] & 0x80)
    pred_h = H.can_be_hurt(prev) and any(H.hurts(cur, dict(en, x=prev[0x460 + en['slot']], y=prev[0x480 + en['slot']])) for en in H.enemies(prev))
    if kb and pred_h: hu_tp += 1
    elif kb: hu_fn += 1; print("hurt FN", f0 + t)
    elif pred_h: hu_fp += 1
print(f"sword: TP {sw_tp} FN {sw_fn} FP {sw_fp} | hurt: TP {hu_tp} FN {hu_fn} FP {hu_fp}")
