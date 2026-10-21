import os

ROOT = ""


def patch(path, reps):
    p = ROOT + path
    s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)


patch("contra/stages/base_plan.py", [
    ("              air=None, plated=()):", "              air=None, plated=(), jump_y=None):"),
    ("    def outcome_air(t, k, hps):", '''    def outcomes_jump(ta, k, hps, ya):
        live = tuple((e.eid, e.track[ta][0], e.track[ta][1],
                      (2 if hps[e.eid] > 8 else 5) if e.eid in plated else e.code) for e in by_slot
                     if hps[e.eid] > 0 and ta in e.track and e.track[ta][2] and (ta, e.eid) not in forbid
                     and ta >= not_before.get(e.eid, 0))
        key = (k, live, ya)
        r = ocache.get(key)
        if r is not None:
            return r
        res = {}
        for px in range(PXMIN, PXMAX + 1):
            c = (3 * px + 640) // 8
            used = 0
            hits = []
            for eid, ex, ey, code in live:
                for j in range(k - 1, -1, -1):
                    if not (used >> j & 1) and in_box(c + PELLET_DX[j], ya, ex, ey, code):
                        used |= 1 << j
                        hits.append((eid, j))
                        break
            m = res.setdefault(tuple(hits), [0])
            m[0] |= 1 << (px - PXMIN)
        r = {hk: m[0] for hk, m in res.items()}
        ocache[key] = r
        return r

    J = len(jump_y) if jump_y else 0

    def outcome_air(t, k, hps):'''),
    ("    states = {(cd0, start_slots, hp0): ((0, R0, 0, 0, 0, 0) if face0 else (R0, 0, 0, 0, 0, 0), None)}",
     "    states = {(cd0, start_slots, hp0, 0): ((0, R0, 0, 0, 0, 0) if face0 else (R0, 0, 0, 0, 0, 0), None)}"),
    ("        for (cd, slots, hps), (R, back) in states.items():",
     "        for (cd, slots, hps, jp), (R, back) in states.items():"),
    ('''            put((min(cd + 1, CAP), ns, hps), dilate(R) if (cd >= 2 and t >= t_start) else R, back)
            nfree = ns.count(0)''', '''            njp = 0 if (jp == 0 or jp >= J) else jp + 1
            put((min(cd + 1, CAP), ns, hps, njp), dilate(R) if (cd >= 2 and t >= t_start and jp == 0) else R, back)
            nfree = ns.count(0)
            if J and jp == 0 and t >= t_start and cd >= 2 and (R[0] | R[1]):
                put((min(cd + 1, CAP), ns, hps, 1), (R[0], R[1], 0, 0, 0, 0), (t, 0, R[0], R[1], (), 9, back))
            if jp:
                if cd >= CAP and nfree and t not in no_press:
                    k = min(5, nfree)
                    ya = min(jump_y[jp - 1], 152) - 40
                    for hk, m in outcomes_jump(t + FLIGHT, k, hps, ya).items():
                        aR, aL = R[0] & m, R[1] & m
                        if not (aR or aL):
                            continue
                        h = len(hk)
                        nh = list(hps)
                        for eid, _ in hk:
                            nh[eid] -= 1
                        nh = tuple(nh)
                        nslots = tuple(sorted(ns[k:] + (t + BUSY_HIT,) * h + (t + BUSY_MISS,) * (k - h)))
                        nb = (t, k, aR, aL, hk, 3, back)
                        if all(nh[c] <= 0 for c in cores):
                            best.append((t + FLIGHT, nb))
                            best.sort(key=lambda x: x[0])
                            del best[ntop:]
                            if len(best) >= ntop:
                                best_fin = best[-1][0] + 1
                            continue
                        put((1, nslots, nh, njp), (aR, aL, 0, 0, 0, 0), nb)
                continue'''),
    ("                    put((1, nslots, tuple(nh)), R, (t, k, 0, 0, hk, 2, back))",
     "                    put((1, nslots, tuple(nh), 0), R, (t, k, 0, 0, hk, 2, back))"),
    ("                    put((1, nslots, nh), (aR, aL, 0, 0, 0, 0), nb)\n        if len(nxt) > beam:",
     "                    put((1, nslots, nh, 0), (aR, aL, 0, 0, 0, 0), nb)\n        if len(nxt) > beam:"),
    ("                (cd, slots, hps), _ = item\n", "                (cd, slots, hps, jp), _ = item\n"),
    ("str(p[1]) + 'sca'[p[5]]", "str(p[1]) + {0: 's', 1: 'c', 2: 'a', 3: 'j', 9: 'J'}[p[5]]"),
])

patch("contra/stages/base_room.py", [
    ('''                for (qx, qf), (c, _) in prev.items():
                    need = sum(n2 for _, n2 in move_script(qx, qf, px, f))
                    if need <= dt - 2 and c + need < bestc:''', '''                for (qx, qf), (c, _) in prev.items():
                    need = sum(n2 for _, n2 in move_script(qx, qf, px, f))
                    if pose == 3 and need:
                        continue
                    if need <= dt - 2 and c + need < bestc:'''),
    ('''            if pressing or holding:
                row.append("B")''', '''            if (pressing and presses[pi][1] == 0) or (holding and presses[pi - 1][1] == 0):
                row.append("A")
            elif pressing or holding:
                row.append("B")'''),
    ('''            elif crouch and not row and T >= T_land and (S.pad.len["Down"] or nextT - (T + 1) >= 2''',
     '''            elif crouch and not row and T >= T_land and not s["jump"] and (S.pad.len["Down"] or nextT - (T + 1) >= 2'''),
    ('''                (pT, k, mR, mL, hk, pose) = presses[pi]
                nb_before = len(bullets(sp))
                new = [b for b in bullets(s) if b[2] == 21]''', '''                (pT, k, mR, mL, hk, pose) = presses[pi]
                new = [b for b in bullets(s) if b[2] == 21]
                if k == 0:
                    if not s["jump"]:
                        res.update(T=T, why="no jump")
                        return "nopress", res
                    pi += 1
                    continue'''),
    ("                if len(new) != k or (pose != 2 and new and new[0][5] != (156 if pose else 144)):",
     "                if len(new) != k or (pose < 2 and new and new[0][5] != (156 if pose else 144)):"),
    ('''        plated = [e.eid for e in ents if e.kind == "core" and e.attr & 4]\n''',
     '''        plated = [e.eid for e in ents if e.kind == "core" and e.attr & 4]
        jump_y = None
        for e in ents:
            if e.kind == "core" and not (e.attr & 4):
                x0, y0, _ = e.track[min(e.track)]
                if not any(bp.in_box(x0, yy, x0, y0, 5) for yy in (bp.STAND_Y, bp.CROUCH_Y)):
                    jump_y = self.jump_table(snap0, T_land)
                    self.say(f"   core at Y {y0} needs jump shots; jump lasts {len(jump_y)} frames")
                    break
'''),
    ("not_before=nb4, air=air, plated=plated,", "not_before=nb4, air=air, plated=plated, jump_y=jump_y,"),
    ("    # -- one attempt at a plan", '''    def jump_table(self, snap0, T_land):
        """Player Y at the end of each frame of a standing jump (index 0 = the frame A is first read)."""
        S = self.S
        S.restore(snap0)
        T = 0
        while T < T_land + 2:
            if not S.step(())["lagged"]:
                T += 1
        ys = []
        for i in range(80):
            s = S.step(S.pad.fix(("A",) if i < 2 else ()))
            if s["lagged"]:
                continue
            ys.append(s["y"])
            if i > 3 and not s["jump"]:
                break
        S.restore(snap0)
        return ys[:-1] if ys else None

    # -- one attempt at a plan'''),
])
print("patched")
