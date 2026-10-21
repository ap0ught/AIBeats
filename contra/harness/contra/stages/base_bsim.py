"""Exact offline model of a base boss screen (stage 2 Eye, stage 4 helmets): player, Spread bullets, platings, wall
cannons, the Eye and the two helmets, written from the disassembly (bank6.asm fire/bullet code, bank7.asm collision
and plating/cannon routines, bank0.asm boss_eye / boss_gemini routines) and checked frame by frame against RAM
captures of real fights (tools/s4_simcheck.py).

One Sim.step(dpad, a_new, b_new) = one non-lag game frame, in the game's own order:
aim -> fire (from the position before this frame's move) -> bullets move -> player moves -> enemies, slot 15 down
to 0: routine, then at most one bullet (highest bullet slot first) is consumed by each enemy whose collision is on.

Not modelled: anything that can hurt Bill (cannon bullets, soldiers, the Eye's rings, the helmets' bubbles), lag
frames, and presses the game does not see. The executor (base_bexec.py) watches the emulator for those.
"""
from __future__ import annotations

# Spread + Rapid velocity table, 32 directions (0 = up, 8 = right, 16 = down, 24 = left), 8.8 fixed point
_VXR = [0x0000, 0x00AB, 0x0153, 0x01F1, 0x0279, 0x02E6, 0x033A, 0x036E, 0x037C, 0x036E, 0x033A, 0x02E6, 0x0279,
        0x01F1, 0x0153, 0x00AB, 0x0000, 0xFF55, 0xFEAD, 0xFE0F, 0xFD87, 0xFD1A, 0xFCC6, 0xFC92, 0xFC84, 0xFC92,
        0xFCC6, 0xFD1A, 0xFD87, 0xFE0F, 0xFEAD, 0xFF55]
VX = list(_VXR)
VY = [_VXR[(i - 8) % 32] for i in range(32)]
PELLET_MOD = (0, 1, -1, 2, -2)
# aim code by d-pad nibble (bit0 Right, bit1 Left, bit2 Down, bit3 Up) on the indoor boss screen
AIM_G = (0, 2, 7, 0, 0, 2, 7, 2, 0, 1, 8, 2, 7, 2, 7, 2)
AIM_J = (0, 2, 7, 0, 10, 3, 6, 2, 0, 1, 8, 2, 7, 2, 7, 2)
AIM_BASE = {0: 0, 1: 4, 2: 8, 3: 12, 4: 8, 5: 24, 6: 20, 7: 24, 8: 28, 9: 0, 10: 0, 11: 16}
MUZ_G = {0: (-1, -24), 1: (15, -16), 2: (16, -6), 3: (15, 8), 4: (16, 11), 5: (-16, 11), 6: (-15, 8), 7: (-16, -6),
         8: (-15, -16), 9: (-1, -24)}
MUZ_J = {0: (0, -16), 1: (15, -15), 2: (16, 0), 3: (15, 15), 4: (0, 16), 5: (0, 16), 6: (-15, 15), 7: (-16, 0),
         8: (-15, -15), 9: (0, -16), 10: (0, -16), 11: (0, -16)}
R, L, D, U = 1, 2, 4, 8
GROUND_Y = 201
HZ_MARGIN = 0            # extra pixels kept between Bill and a cannon bullet (set > 0 for planning)
XMIN_BLOCK, XMAX_BLOCK = 0x20, 0xE0      # no move left when x < 0x20, no move right when x >= 0xE0
T_PLATE, T_CANNON, T_EYE, T_HELMET = 0x0A, 0x08, 0x10, 0x1C
T_RING = 0x1B
# the Eye's ring: aim index by (player Y - Eye Y) >> 5 (rows) and |dx| (see get_quadrant_aim_dir, quadrant_aim_dir_01)
_RING_ROWS = ((0x00, 0x00, 0x00, 0x00), (0x63, 0x21, 0x11, 0x11), (0x64, 0x32, 0x21, 0x11), (0x65, 0x43, 0x22, 0x22),
              (0x65, 0x44, 0x33, 0x22), (0x65, 0x54, 0x33, 0x32), (0x65, 0x54, 0x43, 0x33), (0x65, 0x54, 0x44, 0x33))
_RING_FRACT = ((0x00, 0xFF), (0x42, 0xF7), (0x80, 0xDD), (0xB5, 0xB5), (0xDD, 0x80), (0xF7, 0x42), (0xFF, 0x00))   # (Y, X)


def _speed6(f):
    h = f >> 1
    return f + (((h >> 1) + h) & 0xFF)


def ring_velocity(ex, ey, px, py):
    """(vx, vy) 8.8 of a ring fired from (ex, ey) at a player at (px, py), speed code 6."""
    dy = py - ey
    up = dy < 0
    row = (abs(dy) & 0xFF) >> 5
    dx = px - ex
    left = dx < 0
    dx = abs(dx)
    b = _RING_ROWS[row][dx >> 6]
    aim = (b & 0x0F) if dx & 0x20 else (b >> 4)
    fy, fx = _RING_FRACT[aim]
    vx, vy = _speed6(fx), _speed6(fy)
    return (-vx if left else vx), (-vy if up else vy)
# enemy record layout (plain lists; index constants)
E_T, E_SLOT, E_X, E_Y, E_R, E_D, E_HP, E_COL, E_FR, E_V1, E_V4, E_OFF, E_OFR, E_DIR, E_ATK, E_XA = range(16)


class Sim:
    __slots__ = ("fc", "px", "py", "pys", "pvy", "jump", "pdir", "bx", "by", "bvx", "bvy", "br", "bt", "en",
                 "plates", "cores", "bossdef", "need", "attack", "unsafe", "nlive", "hits", "t", "shots", "hz", "dead", "rg")

    def __init__(self):
        self.fc = 0
        self.px, self.py, self.pys, self.pvy, self.jump, self.pdir = 128, GROUND_Y, 0, 0, 0, 0
        self.bx = [0] * 10      # X position 8.8 (pixel << 8 | accumulator); the accumulator survives the bullet
        self.by = [0] * 10
        self.bvx = [0] * 10
        self.bvy = [0] * 10
        self.br = [0] * 10      # 0 free, 1 flying, 2 hit (ring, slot still busy)
        self.bt = [0] * 10
        self.en = []            # enemy records, slot descending
        self.plates = 0
        self.cores = 0
        self.bossdef = 0
        self.need = 3           # platings the final part waits for
        self.attack = 1
        self.unsafe = 0         # set when a part fired something this model does not track
        self.nlive = 0
        self.hits = 0           # damaging hits so far (for scoring)
        self.t = 0              # frames stepped
        self.shots = 0
        self.hz = []            # cannon bullets in flight: [x 8.8, y 8.8, vx, vy]
        self.dead = 0
        self.rg = []            # the Eye's fire rings: [x 8.8, y 8.8, vx, vy, hp, collides, new]

    def copy(self):
        s = Sim.__new__(Sim)
        s.fc, s.px, s.py, s.pys, s.pvy, s.jump, s.pdir = self.fc, self.px, self.py, self.pys, self.pvy, self.jump, self.pdir
        s.bx, s.by, s.bvx, s.bvy, s.br, s.bt = self.bx[:], self.by[:], self.bvx[:], self.bvy[:], self.br[:], self.bt[:]
        s.en = [e[:] for e in self.en]
        s.plates, s.cores, s.bossdef, s.need, s.attack = self.plates, self.cores, self.bossdef, self.need, self.attack
        s.unsafe, s.nlive, s.hits, s.t, s.shots = self.unsafe, self.nlive, self.hits, self.t, self.shots
        s.hz = [h[:] for h in self.hz] if self.hz else []
        s.dead = self.dead
        s.rg = [h[:] for h in self.rg] if self.rg else []
        return s

    # -- loading from RAM -------------------------------------------------------------------------------------------
    @classmethod
    def from_ram(cls, m, need=None):
        """m: the 2 KB of RAM after some frame (bytes-like)."""
        m = bytes(m)
        s = cls()
        s.fc = m[0x1A]
        s.px, s.py, s.pys = m[0x334], m[0x31A], m[0x94]
        v = (m[0xC6] << 8) | m[0xC4]
        s.pvy = v - 65536 if v >= 32768 else v
        js = m[0xA0]
        s.jump = 1 if js else 0
        s.pdir = 1 if js & 0x20 else (-1 if js & 0x40 else 0)
        for i in range(10):
            s.bx[i] = (m[0x3C8 + i] << 8) | m[0x3A8 + i]
            s.by[i] = (m[0x3B8 + i] << 8) | m[0x398 + i]
            if m[0x388 + i]:
                vx = (m[0x408 + i] << 8) | m[0x3E8 + i]
                vy = (m[0x3F8 + i] << 8) | m[0x3D8 + i]
                s.bvx[i] = vx - 65536 if vx >= 32768 else vx
                s.bvy[i] = vy - 65536 if vy >= 32768 else vy
                r = m[0x438 + i]
                s.br[i] = 1 if r <= 1 else 2
                s.bt[i] = m[0x418 + i]
        s.nlive = sum(1 for r in s.br if r == 1)
        s.plates, s.cores, s.bossdef, s.attack = m[0x87], m[0x86], m[0x3B], m[0x8E]
        types = set()
        for k in range(15, -1, -1):
            rt, t = m[0x4B8 + k], m[0x528 + k]
            if rt and t == 1:
                vx = (m[0x508 + k] << 8) | m[0x518 + k]
                vy = (m[0x4E8 + k] << 8) | m[0x4F8 + k]
                s.hz.append([(m[0x33E + k] << 8) | m[0x4D8 + k], (m[0x324 + k] << 8) | m[0x4C8 + k],
                             vx - 65536 if vx >= 32768 else vx, vy - 65536 if vy >= 32768 else vy])
            if rt == 2 and t == T_RING:
                vx = (m[0x508 + k] << 8) | m[0x518 + k]
                vy = (m[0x4E8 + k] << 8) | m[0x4F8 + k]
                s.rg.append([(m[0x33E + k] << 8) | m[0x4D8 + k], (m[0x324 + k] << 8) | m[0x4C8 + k],
                             vx - 65536 if vx >= 32768 else vx, vy - 65536 if vy >= 32768 else vy,
                             m[0x578 + k], 0 if m[0x598 + k] & 0x80 else 1, 0])
            if not rt or t not in (T_PLATE, T_CANNON, T_EYE, T_HELMET):
                continue
            types.add(t)
            e = [0] * 16
            e[E_T], e[E_SLOT], e[E_X], e[E_Y], e[E_R], e[E_D] = t, k, m[0x33E + k], m[0x324 + k], rt, m[0x538 + k]
            e[E_HP] = m[0x578 + k]
            e[E_COL] = 0 if (m[0x598 + k] & 0x80) or not m[0x30A + k] else 1
            e[E_FR], e[E_V1], e[E_V4] = m[0x568 + k], m[0x5B8 + k], m[0x5E8 + k]
            e[E_OFF], e[E_OFR], e[E_DIR], e[E_ATK] = m[0x4E8 + k], m[0x4F8 + k], m[0x508 + k], m[0x558 + k]
            e[E_XA] = m[0x4D8 + k]
            if t == T_EYE:
                e[E_OFR] = m[0x518 + k]          # the Eye really moves: X velocity fraction / whole in OFR / DIR
            s.en.append(e)
        s.need = need if need is not None else (4 if T_EYE in types else 3)
        return s

    # -- one frame --------------------------------------------------------------------------------------------------
    def step(self, dpad=0, a_new=0, b_new=0):
        self.t += 1
        self.fc = fc = (self.fc + 1) & 0xFF
        br, bx, by = self.br, self.bx, self.by
        px, py, jump = self.px, self.py, self.jump
        # fire (position before this frame's move, aim from this frame's d-pad)
        new = None
        if b_new:
            aim = (AIM_J if jump else AIM_G)[dpad]
            mx, my = (MUZ_J if jump else MUZ_G)[aim]
            base = AIM_BASE[aim]
            new = []
            n = 0
            for i in range(10):
                if br[i] == 0:
                    new.append((i, (base + PELLET_MOD[n]) & 31))
                    n += 1
                    if n == 5:
                        break
            sx, sy = (px + mx) & 0xFF, (py + my) & 0xFF
        # bullets
        if self.nlive or 2 in br:
            bvx, bvy, bt = self.bvx, self.bvy, self.bt
            nl = 0
            for i in range(10):
                r = br[i]
                if r == 1:
                    x = (bx[i] + bvx[i]) & 0xFFFF
                    y = (by[i] + bvy[i]) & 0xFFFF
                    bx[i] = x
                    by[i] = y
                    if x < 0x500 or x >= 0xFB00 or y < 0x500 or y >= 0xE800:
                        br[i] = 0
                    else:
                        nl += 1
                elif r == 2:
                    bt[i] -= 1
                    if bt[i] <= 0:
                        br[i] = 0
            self.nlive = nl
        if new:
            self.shots += 1
            for i, d in new:
                bx[i] = (sx << 8) | (bx[i] & 0xFF)
                by[i] = (sy << 8) | (by[i] & 0xFF)
                self.bvx[i] = VX[d] - 65536 if VX[d] >= 32768 else VX[d]
                self.bvy[i] = VY[d] - 65536 if VY[d] >= 32768 else VY[d]
                br[i] = 1
            self.nlive += len(new)
        # player
        if jump:
            if self.pvy >= 0 and py > 200:
                self.py = GROUND_Y
                self.pvy = 0
                self.jump = 0
            else:
                self.pvy += 0x23
                y16 = ((py << 8) | self.pys) + self.pvy
                self.py = (y16 >> 8) & 0xFF
                self.pys = y16 & 0xFF
            if dpad & R:
                self.pdir = 1
            if dpad & L:
                self.pdir = -1
            d = self.pdir
            if d > 0:
                if px < XMAX_BLOCK:
                    self.px = px + 1
            elif d < 0:
                if px >= XMIN_BLOCK:
                    self.px = px - 1
            if not self.jump:
                self.pdir = 0
        elif a_new and (dpad & 7) != 4:
            self.jump = 1
            self.pvy = -0x410
            self.pdir = 0
        else:
            if dpad & L:
                if px >= XMIN_BLOCK:
                    self.px = px - 1
            elif dpad & R:
                if px < XMAX_BLOCK:
                    self.px = px + 1
        # enemies
        draws = 0
        fired = None
        nlive = self.nlive
        for e in self.en:
            t = e[0]
            r = e[E_R]
            if t == T_HELMET:
                if r == 3:
                    if self.attack:
                        e[E_ATK] = (e[E_ATK] - 1) & 0xFF
                        if e[E_ATK] == 0:
                            self.unsafe = 1          # spinning bubbles (and a reseed of the random number)
                    moving = True
                    if e[E_D]:
                        e[E_D] -= 1
                        if e[E_D]:
                            moving = False
                        else:
                            e[E_COL] = 0
                    if moving:
                        fr = e[E_OFR] + 0x80
                        e[E_OFR] = fr & 0xFF
                        off = (e[E_OFF] + e[E_DIR] + (fr >> 8)) & 0xFF
                        e[E_OFF] = off
                        if e[E_DIR] < 0x80:
                            if off >= 0x30:
                                e[E_D] = 0x20
                                e[E_DIR] = 0xFF
                        elif off >= 0x80:
                            e[E_OFF] = 0
                            e[E_OFR] = 0
                            e[E_COL] = 1
                            e[E_D] = 0x30
                            e[E_DIR] = 0
                    e[E_X] = (e[E_V1] + e[E_OFF]) & 0xFF if not fc & 1 else (e[E_V1] - e[E_OFF]) & 0xFF
                elif r == 4:
                    if e[E_D]:
                        e[E_D] -= 1
                    e[E_V4] -= 1
                    if e[E_V4] == 0:
                        e[E_R] = 5
                    else:
                        e[E_HP] = 1
                        e[E_R] = 3
                elif r == 2:
                    if self.plates >= self.need:
                        e[E_D] -= 1
                        if e[E_D] == 0:
                            e[E_ATK] = 0xA0
                            e[E_COL] = 1
                            e[E_D] = 0x20
                            e[E_R] = 3
                elif r == 5:
                    self.cores -= 1
                    e[E_COL] = 0
                    e[E_R] = 6
                    if self.cores == 0:
                        self.bossdef = 1
                elif r == 1:
                    e[E_V4] = 10
                    e[E_V1] = e[E_X]
                    e[E_D] = 0x40
                    e[E_ATK] = 0x80
                    e[E_R] = 2
            elif t == T_PLATE:
                if r == 2:
                    e[E_D] = (e[E_D] - 1) & 0xFF
                    if e[E_D] == 0:
                        if draws >= 2:
                            e[E_D] = 1
                        else:
                            draws += 1
                            e[E_D] = 4
                            e[E_FR] += 1
                            if e[E_FR] >= 2:
                                e[E_HP] = 10
                                e[E_R] = 3
                elif r == 4:
                    if draws < 2:
                        draws += 1
                        self.plates += 1
                        e[E_R] = 5
                elif r == 5:
                    e[E_COL] = 0
                    e[E_R] = 6
                elif r == 1:
                    e[E_D] = 0x80
                    e[E_R] = 2
            elif t == T_CANNON:
                if r == 2:
                    if self.attack:
                        e[E_D] = (e[E_D] - 1) & 0xFF
                        if e[E_D] == 0:
                            if draws >= 2:
                                e[E_D] = 1
                            else:
                                draws += 1
                                e[E_D] = 6
                                if e[E_FR] >= 2:
                                    e[E_HP] = e[E_V1]
                                    e[E_ATK] = 4
                                    e[E_D] = 0x40
                                    e[E_R] = 3
                                else:
                                    e[E_FR] += 1
                elif r == 3:
                    if e[E_ATK]:
                        e[E_ATK] -= 1
                        if e[E_ATK] == 0:      # three bullets, fixed directions
                            cx, cy = e[E_X], e[E_Y] + 8
                            if fired is None:
                                fired = []
                            fired += [((cx + 8) << 8, cy << 8, 0xF0, 0x19D), (cx << 8, cy << 8, 0, 0x1DC),
                                      ((cx - 8) << 8, cy << 8, -0xF0, 0x19D)]
                    e[E_D] = (e[E_D] - 1) & 0xFF
                    if e[E_D] == 0:
                        e[E_V1] = e[E_HP]
                        e[E_HP] = 0xF1
                        e[E_D] = 6
                        e[E_R] = 4
                elif r == 4:
                    e[E_D] = (e[E_D] - 1) & 0xFF
                    if e[E_D] == 0:
                        if draws >= 2:
                            e[E_D] = 1
                        else:
                            draws += 1
                            e[E_D] = 6
                            if e[E_FR] == 0:
                                e[E_D] = 0x60
                                e[E_R] = 2
                            else:
                                e[E_FR] -= 1
                elif r == 5:
                    if draws < 2:
                        draws += 1
                        e[E_R] = 6
                elif r == 6:
                    e[E_COL] = 0
                    e[E_R] = 7
                elif r == 1:
                    e[E_V1] = 8
                    e[E_D] = 0x50
                    e[E_R] = 2
            elif t == T_EYE:
                if r == 3:
                    if e[E_D]:
                        e[E_D] -= 1
                    xa = e[E_XA] + e[E_OFR]              # E_OFR holds the X velocity fraction, E_DIR the whole part
                    e[E_XA] = xa & 0xFF
                    x = (e[E_X] + e[E_DIR] + (xa >> 8)) & 0xFF
                    e[E_X] = x
                    if e[E_DIR] < 0x80:
                        if x >= 0xB0:
                            v = (-((e[E_DIR] << 8) | e[E_OFR])) & 0xFFFF
                            e[E_DIR], e[E_OFR] = v >> 8, v & 0xFF
                    elif x < 0x50:
                        v = (-((e[E_DIR] << 8) | e[E_OFR])) & 0xFFFF
                        e[E_DIR], e[E_OFR] = v >> 8, v & 0xFF
                    if self.attack:
                        e[E_ATK] = (e[E_ATK] - 1) & 0xFF
                        if e[E_ATK] == 0:
                            e[E_ATK] = 0x28
                            vx, vy = ring_velocity(e[E_X], e[E_Y], self.px, self.py)
                            self.rg.append([e[E_X] << 8, e[E_Y] << 8, vx, vy, 2, 0, 1])
                elif r == 4:
                    e[E_V1] -= 1
                    if e[E_V1] == 0:
                        e[E_R] = 5
                    else:
                        e[E_HP] = 1
                        e[E_D] = 0x20
                        e[E_R] = 3
                elif r == 2:
                    if self.plates >= self.need:
                        e[E_D] -= 1
                        if e[E_D] == 0:
                            e[E_DIR], e[E_OFR] = 1, 0x40
                            e[E_V1] = 0x10
                            e[E_COL] = 1
                            e[E_ATK] = 0x20
                            e[E_D] = 0xC0
                            e[E_R] = 3
                elif r == 5:
                    self.bossdef = 1
                    e[E_COL] = 0
                    e[E_R] = 6
                elif r == 1:
                    e[E_D] = 0x40
                    e[E_R] = 2
            # bullet test
            if nlive and e[E_COL]:
                x0 = (e[E_X] - 10) << 8
                x1 = (e[E_X] + 12) << 8
                y0 = (e[E_Y] - 10) << 8
                y1 = (e[E_Y] + 12) << 8
                for i in (9, 8, 7, 6, 5, 4, 3, 2, 1, 0):
                    if br[i] == 1 and y0 <= by[i] < y1 and x0 <= bx[i] < x1:
                        br[i] = 2
                        self.bt[i] = 6
                        nlive -= 1
                        hp = e[E_HP]
                        if 0 < hp < 0xF0:
                            hp -= 1
                            e[E_HP] = hp
                            self.hits += 1
                            if hp == 0:
                                if t == T_PLATE:
                                    e[E_R] = 4
                                elif t == T_CANNON:
                                    e[E_R] = 5
                                elif e[E_R] < 4:
                                    e[E_R] = 4
                        break
        if self.rg:
            px, py = self.px, self.py
            br, bx, by = self.br, self.bx, self.by
            keep = []
            for g in self.rg:
                if g[6]:
                    g[6] = 0                    # created this frame (routine 0): it only takes its aim
                    keep.append(g)
                    continue
                if g[4] <= 0:
                    continue                    # destroyed last frame
                if (g[1] >> 8) >= 0x48:
                    g[5] = 1
                g[0] += g[2]
                g[1] += g[3]
                gx, gy = g[0] >> 8, g[1] >> 8
                if gy >= 0xE8 or gx < 8 or gx >= 0xF8:
                    continue
                keep.append(g)
                if g[5]:
                    if self.jump:
                        hit = -22 <= py - gy <= 13 and -18 <= px - gx <= 17
                    else:
                        hit = -29 <= py - gy <= 27 and -18 <= px - gx <= 17
                    if hit:
                        self.dead = 1
                    if nlive:
                        x0, x1, y0, y1 = (gx - 16) << 8, (gx + 18) << 8, (gy - 16) << 8, (gy + 18) << 8
                        for i in (9, 8, 7, 6, 5, 4, 3, 2, 1, 0):
                            if br[i] == 1 and y0 <= by[i] < y1 and x0 <= bx[i] < x1:
                                br[i] = 2
                                self.bt[i] = 6
                                nlive -= 1
                                g[4] -= 1
                                break
            self.rg = keep
        self.nlive = nlive
        if self.hz or fired:
            px, py = self.px, self.py
            if self.jump:
                dy0, dy1, dx0, dx1 = -2 - HZ_MARGIN, 11 + HZ_MARGIN, -6 - HZ_MARGIN, 7 + HZ_MARGIN
            else:
                dy0, dy1, dx0, dx1 = -16 - HZ_MARGIN, 18 + HZ_MARGIN, -6 - HZ_MARGIN, 7 + HZ_MARGIN
            keep = []
            for h in self.hz:
                h[0] += h[2]
                h[1] += h[3]
                hx, hy = h[0] >> 8, h[1] >> 8
                if hy >= 0xE8 or hx < 8 or hx >= 0xF8:
                    continue
                keep.append(h)
                if dy0 <= hy - py <= dy1 and dx0 <= hx - px <= dx1:
                    self.dead = 1
            if fired:
                for f in fired:
                    keep.append(list(f))
            self.hz = keep

    # -- views ------------------------------------------------------------------------------------------------------
    def free_slots(self):
        return self.br.count(0)

    def hp_left(self):
        """(platings HP, final part HP, cannon HP) still to remove."""
        p = f = c = 0
        for e in self.en:
            t = e[0]
            if t == T_PLATE:
                if e[E_R] <= 3:
                    p += 10 if e[E_HP] >= 0xF0 else e[E_HP]
            elif t == T_HELMET:
                if e[E_R] <= 4:
                    f += e[E_V4] - (1 if e[E_R] == 4 else 0) if e[E_R] >= 2 else 10
            elif t == T_EYE:
                if e[E_R] <= 4:
                    f += (e[E_V1] - (1 if e[E_R] == 4 else 0)) if e[E_R] >= 3 else 16
            elif t == T_CANNON:
                if e[E_R] <= 4:
                    c += e[E_HP] if e[E_HP] < 0xF0 else e[E_V1]
        return p, f, c

    def describe(self):
        out = [f"t{self.t} fc{self.fc} P({self.px},{self.py}.{self.pys:02x} vy{self.pvy} j{self.jump} d{self.pdir}) "
               f"pl{self.plates} cr{self.cores} bd{self.bossdef}"]
        for e in self.en:
            out.append(f"e{e[E_SLOT]}:t{e[0]:02x} r{e[E_R]} hp{e[E_HP]:02x} x{e[E_X]} d{e[E_D]:02x} c{e[E_COL]} "
                       f"v1={e[E_V1]} v4={e[E_V4]} off={e[E_OFF]:02x}.{e[E_OFR]:02x} dir={e[E_DIR]:02x}")
        out.append("B:" + " ".join(f"{i}:{self.bx[i] >> 8},{self.by[i] >> 8}r{self.br[i]}" for i in range(10) if self.br[i]))
        return " | ".join(out)
