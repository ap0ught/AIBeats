"""Jaquio fireball simulator (bank07 $D3BA-$D43C, home_x $C76D, move_enemy $E04x), calibrated on logs/r4/fb_*.jsonl.
State per fireball: [alive, x, xsub, spd(signed 8.8 as int /256), y, ysub, yspd]."""


def step(fb, rx, ry):
    """one frame for one live fireball; rx, ry = Ryu x (int) and height this frame. Returns False if it left."""
    x, xs, vx, y, ys, vy = fb
    vx += -16 if x >= rx else 16
    vy += 16 if (ry - 8 - y) >= 0 else -16
    # move: sub += frac; pos += spd_hi + carry  (vx, vy kept as 16-bit signed in 1/256 px)
    t = xs + (vx & 0xFF)
    xs = t & 0xFF
    x = x + (vx >> 8) + (t >> 8)
    t = ys + (vy & 0xFF)
    ys = t & 0xFF
    y = y + (vy >> 8) + (t >> 8)
    fb[:] = [x, xs, vx, y, ys, vy]
    if x < 8 or x >= 248 or y < 48 or y >= 248:
        return False
    return True


def hurts(fb, rx, ry):
    x, y = fb[0], fb[3]
    if abs(x - rx) >= 16:
        return False
    d = ry - y
    return (0 <= d < 25) or (0 < -d < 8)


def sword_kills(fb, rx, ry, face):
    x, y = fb[0], fb[3]
    u = (face * (x - rx)) - 16
    if not (0 <= u <= 31):
        return False
    d = y - ry
    return (d >= 0 and d < 16) or (d < 0 and -d < 24)


if __name__ == "__main__":
    import json
    import sys
    L = [json.loads(l) for l in open(sys.argv[1])]
    fbs = {}
    for k in range(1, len(L)):
        d, p = L[k], L[k - 1]
        for s in ("f5", "f6"):
            if d[s][0] == 39 and p[s][0] != 39:   # spawned this row: init from prev row stale subs, pos = J(prev)+-32
                st = [p["jx"] + (32 if s == "f5" else -32), p[s][2], 0, 64, p[s][6], 0]
                fbs[s] = st
                step(st, d["rx"], d["ry"])
            elif s in fbs and d[s][0] == 39:
                step(fbs[s], d["rx"], d["ry"])
            if s in fbs and d[s][0] == 39:
                real = [d[s][1], d[s][2], ((d[s][3] << 8) | d[s][4]) - (65536 if d[s][3] >= 128 else 0), d[s][5], d[s][6], ((d[s][7] << 8) | d[s][8]) - (65536 if d[s][7] >= 128 else 0)]
                if real != fbs[s]:
                    print("MISMATCH row", d["row"], s, "sim", fbs[s], "real", real, "R", d["rx"], d["ry"])
                    fbs[s] = real
    print("done")
