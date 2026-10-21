"""Per-frame RAM/OAM of a captured replay (ramcap.py) and where things are on screen.
Row i = state after input line i+1. Object attribute a of slot s lives at 0x3C1 + a*15 + s (feos's object table)."""
from __future__ import annotations
import numpy as np
from style import LOGS

A = dict(id=0, anim=1, xh=3, xl=4, yh=5, yl=6, zh=7, zl=8, zshad=12, xshad=13, yshad=14, flag=15, state=16, hp=23, xspd=28)


class Cap:
    def __init__(self, name):
        self.ram = np.memmap(LOGS / f"{name}.ram", dtype=np.uint8, mode="r").reshape(-1, 2048)
        self.oam = np.memmap(LOGS / f"{name}.oam", dtype=np.uint8, mode="r").reshape(-1, 256)
        self.n = len(self.ram)

    def r(self, f, addr):
        return int(self.ram[f, addr])

    def a(self, f, attr, s):
        return int(self.ram[f, 0x3C1 + A[attr] * 15 + s])

    def cam(self, f):
        return self.r(f, 0x87) + 256 * self.r(f, 0x88), self.r(f, 0x89) + 256 * self.r(f, 0x8A)

    def obj(self, f, s):
        sx = lambda v: v - 256 if v > 127 else v
        return dict(slot=s, id=self.a(f, "id", s), hp=self.a(f, "hp", s), anim=self.a(f, "anim", s),
                    x=self.a(f, "xl", s) + 256 * sx(self.a(f, "xh", s)),
                    h=self.a(f, "zl", s) + 256 * sx(self.a(f, "zh", s)),
                    yshad=self.a(f, "yshad", s), zshad=self.a(f, "zshad", s), yl=self.a(f, "yl", s),
                    flag=self.a(f, "flag", s), state=self.a(f, "state", s), xspd=self.a(f, "xspd", s))

    def screen(self, f, s):
        """feet point on the NES screen (hitbox.lua: x - camX, y = Yshad - Zshad + 8)"""
        o = self.obj(f, s)
        cx, _ = self.cam(f)
        return o["x"] - cx, o["yshad"] - o["zshad"] + 8

    def sprites(self, f):
        o = self.oam[f]
        return [(int(o[i + 3]), int(o[i]) + 1 - 8, int(o[i + 1]), int(o[i + 2])) for i in range(0, 256, 4) if o[i] < 239]
