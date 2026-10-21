"""Pre-face-2 fight by the TAS's inputs (2026-10-07). Our L12r frame 5218 == TAS 74091 (spring 34, foe 384/95, camy 1616).
Replay TAS inputs from j0 (mapped to our frame 5218 + (j0-74091)), with the walk-left stretch length varied, and report the kill."""
import json, sys
from toads.emulator import BizHawk
T = {int(k): v for k, v in json.load(open('knowledge/tas_l12_f2.json')).items()}
KEY = {"le": "Left", "ri": "Right", "up": "Up", "do": "Down", "A": "A", "B": "B", "se": "Select", "st": "Start"}
import re
def btn(p): return tuple(KEY[k] for k in re.findall(r"le|ri|up|do|se|st|A|B", p)) if p != '-' else ()
ins=[x.replace(',','+') for x in json.load(open('logs/pbeam_L12r.json'))['inputs']]
e = BizHawk(log_name="l12f2tas.log"); e.load("L12p_f5000")
def rd():
    m = e.ram(0, 0x800)
    foe=[(m[0x3FD+q] | m[0x3EE+q] << 8, m[0x439+q], m[0x51A+q]) for q in range(2,15) if m[0x3C1+q]==0x5c]
    sp=[(m[0x3FD+q] | m[0x3EE+q] << 8) for q in range(2,15) if m[0x3C1+q]==0x36]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, h=m[0x439], z=m[0x475], an=m[0x3B5], hp=m[0x51A], foe=foe, sp=sp)
J0 = int(sys.argv[1]) if len(sys.argv) > 1 else 74098
F0 = 5218 + (J0 - 74091)
for f in range(5000, F0): e.step(tuple(v for v in ins[f].split('+') if v), 1)
base = e.msave(); print("ours at", F0, rd(), "TAS", J0, T[J0], flush=True)
results = []
for extra_right in (0, 1, 2, 3):
    for dleft in range(-6, 7, 2):
        e.mload(base); seq = []
        for j in range(J0, 74226):
            p = T[j]["p"]
            if j == J0 and extra_right: seq += [("Right",)] * extra_right
            if j == 74140 and dleft < 0: continue
            seq.append(btn(p))
            if j == 74170 and dleft > 0: seq += [("Left",)] * dleft
        if dleft < 0: 
            # drop |dleft| of the 'le' walk frames
            k = 0; s2 = []
            for b in seq:
                if b == ("Left",) and k < -dleft: k += 1; continue
                s2.append(b)
            seq = s2
        kill = None; hurt = False
        for i, b in enumerate(seq):
            e.step(b, 1); s = rd()
            if s["hp"] < 47: hurt = True; break
            if s["foe"] and s["foe"][0][2] == 0 and kill is None: kill = F0 + i + 1
        s = rd()
        print(f"extraR {extra_right} dleft {dleft:+d}: kill {kill} {'HURT' if hurt else ''} end x {s['x']} h {s['h']} z {s['z']} sp {s['sp']} (TAS 74225: x {T[74225]['x']} h {T[74225]['h']} sp {T[74225]['sp']}; TAS kill 74195 = our {5218+74195-74091})", flush=True)
        results.append((kill or 99999, extra_right, dleft))
print("best", sorted(results)[:3])
e.close()
