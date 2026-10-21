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


patch("contra/stages/base_room.py", [
    ("def choose_path(presses, px0, face0, T0):", "def choose_path(presses, px0, face0, T0, avoid=()):"),
    ('''        for f, m in ((0, mR), (1, mL)):
            for px in bp.mask_list(m):
                bestc, bestp = INF, None''', '''        for f, m in ((0, mR), (1, mL)):
            for px in bp.mask_list(m):
                if pose == 0 and any(t0 <= T <= t1 and x0 <= px <= x1 for (t0, t1, x0, x1) in avoid):
                    continue                 # standing up there at that time was fatal in an earlier attempt
                bestc, bestp = INF, None'''),
    ("    def execute(self, snap0, plan, ents, T_land, crouch=True, up_wait=True):",
     "    def execute(self, snap0, plan, ents, T_land, crouch=True, up_wait=True, avoid=()):"),
    ("        path, bad = choose_path(presses, px_l, f_l, T_land - 1)",
     "        path, bad = choose_path(presses, px_l, f_l, T_land - 1, avoid)"),
    ('''                st, info = self.execute(snap0, plan, ents, T_land)
                self.say(''', '''                avoid = []
                for _try in range(8):
                    # a death while standing up to shoot: same plan, stand somewhere else for those presses
                    st, info = self.execute(snap0, plan, ents, T_land, avoid=avoid)
                    if st != "death":
                        break
                    avoid.append((info["T"] - 8, info["T"] + 2, info["x"] - 8, info["x"] + 8))
                self.say('''),
])
print("patched")
