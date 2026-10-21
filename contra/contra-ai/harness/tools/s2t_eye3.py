"""Third pass, Eye: how many hits can the FIRST jump deliver, if the slots are prepared during the 64-frame wait?

    python tools/s2t_eye3.py <tag> [lane]

Brute force on the exact model from a captured phase-B start (logs/s2t/eye_caps.pkl): Bill walks to the lane and
stands; up to two "blocker" sprays before the jump (pellets that fly through the shut Eye and free their slots at
different times); jump at t_A; presses in the air (straight up) found by a narrow beam. Prints the best lines by
Eye HP left 20 frames after it opens.
"""
import itertools
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages import base_bsim as bs, base_bplan as bp  # noqa: E402

E_R, E_D, E_V1, E_X = bs.E_R, bs.E_D, bs.E_V1, bs.E_X
L, R, U, A, B = 1, 2, 4, 8, 16          # held-mask bits of base_bplan (BTN order Left, Right, Up, A, B)


def eye_hp(s):
    for e in s.en:
        if e[0] == bs.T_EYE:
            return 0 if e[E_R] >= 5 else (16 if e[E_R] < 3 else e[E_V1] - (1 if e[E_R] == 4 else 0))
    return 0


def legal(pad, act):
    return all(bp.PNEXT[pad[k]][act >> k & 1] >= 0 for k in range(5))


def step(s, pad, act):
    dpad, a_new, b_new, pad = bp.sim_inputs(pad, act)
    s.step(dpad, a_new, b_new)
    return pad


def run_script(sim0, pad0, lane, blockers, t_A, n_frames):
    """Walk to the lane, fire the blockers [(frame index, aim)], press A on frame index t_A. Returns (sim, pad,
    acts) after n_frames frames, or None if something is illegal. aim: 'U' up (standing), 'H' horizontal / 'D'
    diagonal in the walking direction."""
    s = sim0.copy()
    pad = tuple(pad0)
    acts = []
    blk = dict(blockers)
    hold_b = hold_u = hold_a = 0
    for i in range(1, n_frames + 1):
        act = 0
        d = lane - s.px
        pl, pr = pad[0], pad[1]
        if not s.jump and i < t_A:
            if bp.P_MUST[pl]:
                act |= L
            elif bp.P_MUST[pr]:
                act |= R
            elif d <= -1 and (bp.P_HELD[pl] or (bp.P_CAN[pl] and d <= -2)):
                act |= L
            elif d >= 1 and (bp.P_HELD[pr] or (bp.P_CAN[pr] and d >= 2)):
                act |= R
        aim = blk.get(i)
        if aim is not None:
            if aim == "U" and act & (L | R):
                return None
            if aim in ("H", "D") and not act & (L | R):
                return None
            hold_b = 2
            if aim == "D":
                hold_u = 2
        if hold_b:
            act |= B
            hold_b -= 1
        if hold_u:
            act |= U
            hold_u -= 1
        if i == t_A:
            hold_a = 2
        if hold_a:
            act |= A
            hold_a -= 1
        if not legal(pad, act):
            return None
        pad = step(s, pad, act)
        acts.append(act)
        if s.dead:
            return None
    return s, pad, acts


def air_beam(s0, pad0, n_frames, width=40, t_stop=None):
    """Narrow beam over B presses only (no d-pad: straight up) for n_frames frames. Returns [(hp, sim, pad, acts)]."""
    layer = [(s0, pad0, [], None)]
    for i in range(n_frames):
        nxt = []
        seen = set()
        for s, pad, acts, val in layer:
            for act in (0, B):
                if act == 0 and bp.P_MUST[pad[4]]:
                    continue
                if not legal(pad, act):
                    continue
                s2 = s.copy()
                sh = s2.shots
                p2 = step(s2, pad, act)
                if s2.dead:
                    continue
                key = (tuple(s2.br), tuple(s2.bx), tuple(s2.by), s2.hits, p2[4])
                if key in seen:
                    continue
                seen.add(key)
                if s2.shots != sh or val is None:
                    r = s2.copy()
                    for _ in range(45):
                        if not r.nlive:
                            break
                        r.step(0, 0, 0)
                    v = (eye_hp(r), -r.br.count(0))
                else:
                    v = val
                nxt.append((s2, p2, acts + [act], v))
        nxt.sort(key=lambda x: x[3])
        layer = nxt[:width]
        if not layer:
            return []
    return [(eye_hp(s), s, pad, acts) for s, pad, acts, v in layer]


if __name__ == "__main__":
    tag = sys.argv[1]
    lanes = [int(x) for x in sys.argv[2:]] or [128]
    c = pickle.load(open(ROOT / "logs" / "s2t" / "eye_caps.pkl", "rb"))[tag]
    sim0 = bs.Sim.from_ram(c["ram"])
    bs.HZ_MARGIN = 2
    pad0 = bp.pad_from_rows(c["rows"])
    eye = next(e for e in sim0.en if e[0] == bs.T_EYE)
    D = eye[E_D]
    print(tag, "Bill", sim0.px, sim0.py, "jump", sim0.jump, "Eye opens in", D, "frames; free slots", sim0.br.count(0))
    t = time.time()
    res = []
    n_try = 0
    for lane in lanes:
        for t_A in range(D - 40, D - 27):
            cands = [()]
            times = range(1, t_A - 1)
            for a, aim in itertools.product(times, "UHD"):
                cands.append(((a, aim),))
            for a, b in itertools.combinations(times, 2):
                if b - a >= 5:
                    for aa, ab in itertools.product("UHD", repeat=2):
                        cands.append(((a, aa), (b, ab)))
            for blk in cands:
                out = run_script(sim0, pad0, lane, blk, t_A, t_A + 12)
                if out is None:
                    continue
                n_try += 1
                s, pad, acts = out
                fin = air_beam(s, pad, D + 20 - (t_A + 12), width=12)
                if fin:
                    hp, s2, p2, a2 = min(fin, key=lambda x: (x[0], -x[1].br.count(0)))
                    res.append((hp, -s2.br.count(0), lane, t_A, blk, acts + a2))
    res.sort(key=lambda x: x[:2])
    print(f"{n_try} scripts in {time.time() - t:.0f} s")
    for hp, nf, lane, t_A, blk, acts in res[:12]:
        presses = [i + 1 for i, a in enumerate(acts) if a & B and (i == 0 or not acts[i - 1] & B)]
        print(f"HP left {hp} at open+20, free slots {-nf}; lane {lane} A at {t_A} (open {t_A - D:+d}) blockers {blk} presses {presses}")
