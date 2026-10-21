"""Track END probe 4 (snapshot + debug pokes, never part of a run): the predictor against the game for other last-hit states.
On up14's last-hit frame the Queen's whirl timer ($4F0), angle ($559), step ($4E1) and height ($43C) are overwritten, the
plain ending is played (no steering: whatever the dice give) and the real T. Bird cut is compared with end_model's number
computed from the same RAM plus the dice that were actually rolled.   -> logs/fix/end_x4.tsv"""
import sys

import end_model as M
from end_tail import Ending, to_last_hit, bt
from toads.emulator import BizHawk, LOGS_DIR

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name="end_x4.log")
e.load("cap14_f46000")
hit = to_last_hit(e, lines, 46000)
base = e.msave()
S = 3
rows = []
cases = [(a, None, None, None) for a in (0, 1, 5, 14, 15, 40, 71, 100, 111, 120, 142, 143, 150, 160, 171, 172, 173, 200, 230, 255)]
cases += [(27, 0, 2, None), (60, 0, -3, None), (150, 0, 2, None), (200, 128, -2, None), (27, None, None, 44), (71, None, None, 44),
          (150, None, None, 44), (27, None, None, 200)]
quiet = lambda *a: None
for a, th, d, qh in cases:
    e.mload(base)
    e.poke(M.T_TMR + S, a)
    if th is not None:
        e.poke(M.T_ANG + S, th)
    if d is not None:
        e.poke(M.T_DIR + S, d & 0xFF)
    if qh is not None:
        e.poke(M.T_HLO + S, qh)
    en = Ending(e, quiet)
    pr = M.predict(en.m0, natural=True)
    en.measure()
    en.best = None
    en._plain_outcome()
    wait_model = en.best["wait"] if en.best else None
    res = en.finish(steer_skip=False)
    model = res["queen_speech_cut"] + res["skip"] + res["lag"] + 340 + (wait_model or 0)
    row = (a, en.hit["theta"], en.hit["d"], en.hit["h"], res["flight"], pr["flight"], res["n1"], pr["n1"], str(en.best["draws"]), wait_model,
           res["wait"], res["skip"], res["lag"], res["tbird_cut"], model, "OK" if model == res["tbird_cut"] else "MISMATCH",
           pr["best"], pr["floor"], pr.get("natural_lo"), pr.get("natural_hi"))
    rows.append(row)
    print(*row, flush=True)
    e.mfree(en.base)
hdr = ("timer theta step qh flight flight_pred n1 n1_pred dice wait_model wait_actual skip lag tail_actual tail_model check "
       "pred_best pred_floor pred_natural_lo pred_natural_hi").split()
(LOGS_DIR / "fix" / "end_x4.tsv").write_text("\t".join(hdr) + "\n" + "\n".join("\t".join(map(str, r)) for r in rows) + "\n")
e.close()
