"""Scripted helmet attack in the model: python tools/s4_script.py <dead> <x> <jump frames rel A, comma> <fire frames rel A, comma>"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import base_bsim as bs
R = np.load("logs/s4/x_cap_p0.npy")
dead, x = int(sys.argv[1]), int(sys.argv[2])
jumps = [int(v) for v in sys.argv[3].split(",") if v]
fires = [int(v) for v in sys.argv[4].split(",") if v]
s = bs.Sim.from_ram(R[230])
for e in s.en:
    if e[0] == bs.T_CANNON and dead:
        e[bs.E_R], e[bs.E_COL] = 7, 0
s.br = [0] * 10; s.nlive = 0
s.jump, s.py, s.pvy, s.pdir, s.px = 0, 201, 0, 0, x
prev = None
for i in range(231, 520):
    rel = i - 286
    sh = s.shots
    s.step(0, rel in jumps, rel in fires)
    hs = [(e[bs.E_V1], e[bs.E_X], e[bs.E_V4], e[bs.E_D], e[bs.E_COL], e[bs.E_OFF], e[bs.E_R]) for e in s.en if e[0] == bs.T_HELMET]
    cur = tuple(h[2] for h in hs) + tuple(h[6] >= 5 for h in hs)
    if cur != prev or s.shots != sh or rel in jumps:
        print(f"A{rel:+4d} P({s.px},{s.py}) j{s.jump} free{s.free_slots()} {'FIRE' if s.shots != sh else '    '} " + " ".join(f"[x{h[1]} hp{h[2]} d{h[3]} c{h[4]} off{h[5]} r{h[6]}]" for h in hs) + f" bd{s.bossdef} unsafe{s.unsafe}")
    prev = cur
    if s.bossdef:
        break
