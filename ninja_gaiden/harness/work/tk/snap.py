"""Replay rows from a state and print the hitbox snapshot (+ screenshot) at chosen row indices.
    python work/tk/snap.py <state> <rows|-> <i,j,k> [--shot name]"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C, hitbox as H
from ng.mode import TICKS
a = sys.argv[1:]
shot = a[a.index('--shot') + 1] if '--shot' in a else None
rows = C.rows_of(a[1]) if a[1] != '-' else []
idx = [int(x) for x in a[2].split(',')]
e = C.open_emu('tk_snap.log')
try:
    e.tick(TICKS); st = e.load(a[0]); pos = 0
    for i in idx:
        if i > pos:
            s = e.run(rows[pos:i]); pos = i
        r = e.ram_all(); s = e.state()
        sn = H.snapshot(r)
        print(f"row {i} frame {s['frame']} room {s['room']} X {C.abs_x(s)} scroll {C.abs_x(s)-s['x']} ryu {sn['ryu']}")
        for en in sn['enemies']: print('   enemy', en)
        for ln in sn['lanterns']: print('   lantern', ln)
        if shot: e.screenshot(f"{shot}_{i}")
finally:
    e.close()
