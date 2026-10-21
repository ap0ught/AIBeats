"""Stage 4 (Base 2) solver: eight rooms + the boss (three platings, then the two helmets) + the exit.

    from contra.stages import s4
    out = s4.solve(emu, "s4/dbg_L", hist=rows_before)      # state = the stage's first frame ($2C == 4)

Same driver as stage 2 (contra/stages/s2.py); only the boss parameters differ.
"""
from __future__ import annotations

from . import base_boss4, s2

# the fight planned on the offline model (base_bfight: both helmets in the first opening); the first builder's
# search (platings by beam, one helmet per opening by a scripted attack) is the fallback
BOSS = dict(fn=s2.planned_boss(base_boss4.solve_boss))


def solve(emu, state, hist=(), verbose=True, beam=12000, save_states=None, boss_width=12, rooms_only=False,
          boss_hold=4, pause=0, rooms3=True):
    return s2.solve(emu, state, hist=hist, verbose=verbose, beam=beam, save_states=save_states,
                    boss_width=boss_width, boss=BOSS, rooms_only=rooms_only, boss_hold=boss_hold, pause=pause,
                    rooms3=rooms3)
