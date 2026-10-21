"""The Dark Queen's ending as a model (track END, 2026-10-09). Everything here was read out of the ROM (bank 0 $D352-$D50B,
$EB49-$EC0B) and checked against 17 replayed fights (end_var.py) - see knowledge/end_timing.md.

After the last hit (object 0x7e -> 0x46 in slot s, normally 3) the game plays, with nothing the player can shorten except
where noted:

    flight     the dead Queen is thrown up at 7 px/frame from where she was hit, falls, bounces once on the floor (h 44) and
               drops off the bottom: 154 frames if she was hit standing on the floor, up to ~170 if hit high. (FIGHT-side.)
    207        countdown ($583+s) after she re-enters as object 0x7e at x 128, below the screen
    N1         rise 1 px/frame for 86 odd-timer frames: 171 or 172 frames
    122        she stands on the tower's tip; then the cut to her speech (level byte 13 -> 254, the FIRST cut)
    skip       9..13 frames before the speech screen polls the pad (dice); a NEW press of A/B/Select on that frame leaves it
    14 (or 15) the level reloads (dice / CPU time again)
    48+172+120 back on the tower: fade in, a second 172-frame rise as a whirlwind, a stand
    wait       then the game counts her whirl timer $4ED+s down to zero and only THEN cuts to Professor T. Bird
               (level byte 13 -> 254, the SECOND cut = the end of the run): 1..256 frames. THIS is the lottery.

The whirl timer ($4ED+s) is the same byte her whirlwind attack uses in the fight. It is frozen from the last hit until the
first rise, then ticks down once per rise frame (343 or 344 of them). Each time it reaches 0 it is reloaded:
    height in 0..127  -> random: (rng$26 & 63) + 32 (+1), direction step (rng$25 & 7) - 3 or - 4       [steerable: any input
                         earlier in the ending changes the dice; the toad is free to move and Select does nothing else]
    otherwise         -> |0xC0 - angle| / 2 with step +-2 (her angle $556+s then lands on 0xC0, and the NEXT reload is 0)
and a reload of 0 is not a reload at all: the byte wraps to 255 and runs 256 frames. Call K the rise frame on which that
final 0 is loaded. Then the wait is K + 84 - N1 frames, and

    frames from the last hit to the T. Bird cut = flight + skip + reload + K + 753      (= flight + K + 776 at best)

K cannot be earlier than the first rise frame with height >= 128 (k128 = 128 - h0, 141..143): the fastest possible ending
is 154 + 9 + 14 + 141 + 753 = 1071 frames after a floor-level last hit (up14: 1168; with its own last hit 1085 at best,
verified as route up14e; the record run: about 1172).
"""
from __future__ import annotations

QID, DEAD = 0x7E, 0x46
T_ID, T_ANG, T_DIR, T_TMR, T_HLO, T_HHI, T_CTR, T_PH = 0x3C1, 0x556, 0x4DE, 0x4ED, 0x439, 0x42A, 0x583, 0x5A1
FLOOR_H = 44
N2 = 172
LAG_MIN = 14                               # frames the level reload takes after the speech (14 or 15: dice / CPU time)
FIXED = 207 + 122 + LAG_MIN + 340          # 683: everything between the pieces that vary (340 = 48 + 172 + 121 - 1)
SKIP_MIN = 9
BIG = 10 ** 9

# FLIGHT[qh] = (frames from the last hit to the respawn 0x46 -> 0x7e, her height at the respawn). Measured by poking her
# height on the hit frame of up14 (end_flight.py -> logs/fix/end_flight.json); the natural samples agree.
FLIGHT: dict[int, tuple[int, int]] = {}


def s8(v: int) -> int:
    return v - 256 if v > 127 else v


def queen_slot(m: bytes):
    for s in range(2, 15):
        if m[T_ID + s] in (QID, DEAD):
            return s
    return None


def det_reload(theta: int):
    """The reload outside heights 0..127: (timer, direction). Timer 0 means 'wraps for 256 frames'."""
    v = (0xC0 - theta - 1) & 0xFF
    if v < 128:
        return v >> 1, 2
    return (v ^ 0xFF) >> 1, -2


def simulate(a: int, theta: int, d: int, h0: int = -15, n1: int = 171, draws=None, stop_at_random: bool = False):
    """Run the whirl timer through both rises. a = $4ED+s, theta = $556+s, d = signed $4DE+s at the last hit.
    draws = list of (timer, direction) for the random reloads in order (what the dice gave, or what steering asks for).
    Returns a dict: K (rise frame of the last 0 reload, None if none), wait (frames of the final count-down), events,
    or, when a random reload has no draw left (or stop_at_random): open=True and need = (rise frame, angle there)."""
    A, th = a & 0xFF, theta & 0xFF
    ev = []
    draws = list(draws or [])
    K = None
    for k in range(1, n1 + N2 + 1):
        h = h0 + k if k <= n1 else 128 + k          # the second rise starts at 156: always >= 128
        th = (th + d) & 0xFF
        A = (A - 1) & 0xFF
        if A == 0:
            if 0 <= h <= 127:
                if stop_at_random or not draws:
                    return {"K": None, "need": (k, th), "events": ev, "open": True}
                A, d = draws.pop(0)
                ev.append((k, "rnd", A, d, th))
            else:
                A, d = det_reload(th)
                ev.append((k, "det", A, d, th))
                if A == 0:
                    K = k
    return {"K": K, "wait": A if A else 256, "A_end": A, "events": ev, "open": False}


def k128(h0: int = -15) -> int:
    return 128 - h0


def tail_frames(flight: int, n1: int, wait: int, skip: int = SKIP_MIN) -> int:
    """Frames from the last hit (the frame the Queen's id turns 0x46) to the T. Bird cut (second level byte 13 -> 254)."""
    return flight + n1 + skip + wait + FIXED


def final_K(z: int, th: int) -> int:
    """K when the timer reaches 0 on rise frame z (height >= 128 there) with angle th."""
    return z + det_reload(th)[0]


def best_draws(a: int, theta: int, d: int, h0: int = -15, n1: int = 171, prefix=None):
    """The shortest final wait reachable when every random reload after `prefix` (the draws already rolled) can be steered
    to any timer 32..96 and any step -4..4. Returns (wait, draws incl. prefix), (BIG, None) if nothing was found.
    Closed form on the next one or two random reloads: K = z + |0xC0 - angle(z)| / 2 once z is at height >= 128."""
    prefix = list(prefix or [])
    r = simulate(a, theta, d, h0, n1, draws=prefix)
    if not r["open"]:
        return r["wait"], prefix
    k0, th0 = r["need"]
    lo = k128(h0)
    best = (BIG, None)
    for R1 in range(32, 97):
        z1 = k0 + R1
        if z1 >= lo:                                      # one steered reload, then deterministic
            for d1 in range(-4, 5):
                K = final_K(z1, (th0 + d1 * R1) & 0xFF)
                if K < best[0]:
                    best = (K, [(R1, d1)])
        elif z1 + 32 <= lo + 16:                          # two steered reloads
            for R2 in range(max(32, lo - z1), min(96, lo - z1 + 16) + 1):
                z2 = z1 + R2
                for d1 in (0, 1, -1, 2, -2, 3, -3, 4, -4):
                    t1 = (th0 + d1 * R1) & 0xFF
                    for d2 in range(-4, 5):
                        K = final_K(z2, (t1 + d2 * R2) & 0xFF)
                        if K < best[0]:
                            best = (K, [(R1, d1), (R2, d2)])
                    if best[0] <= lo:
                        break
                if best[0] <= lo:
                    break
        if best[0] <= max(lo, k0 + 32):
            break
    if best[1] is None:
        return BIG, None
    chk = simulate(a, theta, d, h0, n1, draws=prefix + best[1] + [(64, 0)] * 3)
    return chk["wait"], prefix + best[1]


def natural_range(a: int, theta: int, d: int, h0: int = -15, n1: int = 171):
    """(shortest, mean, longest) final wait when the dice fall anywhere: every random reload uniform in 32..96 x -4..4
    (coarse grid, at most three random reloads)."""
    waits = []
    stack = [[]]
    while stack:
        dr = stack.pop()
        r1 = simulate(a, theta, d, h0, n1, draws=dr)
        if not r1["open"]:
            waits.append(r1["wait"])
        elif len(dr) < 3:
            for R in (32, 40, 48, 56, 64, 72, 80, 88, 96):
                for dd in (-4, -2, 0, 2, 4):
                    stack.append(dr + [(R, dd)])
    if not waits:
        return BIG, BIG, BIG
    return min(waits), sum(waits) / len(waits), max(waits)


def read_hit(m: bytes, s: int | None = None) -> dict:
    """The model's inputs from the RAM of the last-hit frame (or any later frame before the first rise)."""
    s = queen_slot(m) if s is None else s
    h = m[T_HLO + s] + 256 * s8(m[T_HHI + s])
    return {"slot": s, "a": m[T_TMR + s], "theta": m[T_ANG + s], "d": s8(m[T_DIR + s]), "h": h, "t0b": m[0x0B],
            "toad_x": m[0x3FD], "toad_h": m[0x439], "id": m[T_ID + s]}


def flight_of(qh: int):
    """(flight frames, respawn height) for a last hit at Queen height qh."""
    if qh in FLIGHT:
        return FLIGHT[qh]
    if FLIGHT:
        return FLIGHT[min(FLIGHT, key=lambda x: abs(x - qh))]
    import math                                         # ballistic fallback: 9 frozen frames, 7 px/f up, 39/256 px/f^2
    g = 39 / 256
    peak = qh + 49 / (2 * g)
    return int(round(9 + 7 / g + math.sqrt(2 * max(0.0, peak - FLOOR_H) / g) + 53.5)), -15


def predict(m: bytes, qh: int | None = None, skip: int = SKIP_MIN, natural: bool = False) -> dict:
    """PREDICTOR for the fight search. m = RAM (2 KB) of the frame on which the Queen's id turns 0x46 = the last hit (her
    height byte on that frame is still the height she was hit at). Frames from that frame to the T. Bird cut:
        best        with the random reloads steered (what end_tail.py goes for) and the speech left on its 9th frame
        floor       the bound for this hit height (the timer parks on the first rise frame at height >= 128)
        natural_lo / natural_mean / natural_hi   (natural=True; slower) with unsteered dice
    plus the pieces: flight, h0, n1, a (timer), theta, d, wait_best, draws, steerable (False = no dice left to steer).
    T. Bird cut frame = last-hit frame + best. Not modelled: the toad standing within ~25 px of x 128 when the Queen
    rises (rise frames ~38-45) is hit three times and killed: +27 frames; end_tail.py walks it away first."""
    r = read_hit(m)
    qh = r["h"] if qh is None else qh
    flight, h0 = flight_of(qh)
    n1 = 171 if (r["t0b"] + flight) % 2 == 0 else 172
    wait, draws = best_draws(r["a"], r["theta"], r["d"], h0, n1)
    out = {"flight": flight, "h0": h0, "n1": n1, "a": r["a"], "theta": r["theta"], "d": r["d"], "wait_best": wait,
           "draws": draws, "steerable": bool(draws), "best": tail_frames(flight, n1, wait, skip),
           "floor": tail_frames(flight, n1, k128(h0) + 84 - n1, skip), "toad_x": r["toad_x"]}
    if natural:
        lo, mean, hi = natural_range(r["a"], r["theta"], r["d"], h0, n1)
        out["natural_lo"], out["natural_mean"], out["natural_hi"] = (tail_frames(flight, n1, lo, skip),
                                                                     round(tail_frames(flight, n1, 0, skip) + mean, 1),
                                                                     tail_frames(flight, n1, hi, skip))
    return out


def predict_frames(m: bytes) -> int:
    """Just the number: frames from the last-hit frame (RAM m) to the T. Bird cut with the best legal ending."""
    return predict(m)["best"]


def _load_flight():
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parent / "logs" / "fix" / "end_flight.json"
    if p.exists():
        for k, v in json.loads(p.read_text()).items():
            FLIGHT[int(k)] = (v[0], v[1])


_load_flight()
