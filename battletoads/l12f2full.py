"""Face 2 the TAS's way (2026-10-07): from L12r 5225 (== TAS 74098 + toad 5 px left) replay TAS inputs 74098..END with
the banned Left+Right presses swapped (leri -> '', leriA -> SUB), extra Right frames at the start and extra Left walk frames.
Reports the landmarks; env END (default 74825)."""
import json, sys, os, re
from toads.emulator import BizHawk
T = {int(k): v for k, v in json.load(open('knowledge/tas_l12_f2.json')).items()}
KEY = {"le": "Left", "ri": "Right", "up": "Up", "do": "Down", "A": "A", "B": "B", "se": "Select", "st": "Start"}
def btn(p): return tuple(KEY[k] for k in re.findall(r"le|ri|up|do|se|st|A|B", p)) if p != '-' else ()
END = int(os.environ.get("END", 74825)); SUB = os.environ.get("SUB", "A")
XR, DL = int(os.environ.get("XR", 2)), int(os.environ.get("DL", 4))
ins=[x.replace(',','+') for x in json.load(open('logs/pbeam_L12r.json'))['inputs']]
def build(shifts):
    seq = [("Right",)] * XR
    for j in range(74098, END):
        p = T[j]["p"]
        if ('le' in p and 'ri' in p):
            p = p.replace('le', '').replace('ri', '')
            if p == '' or p == 'A': p = {'': '-', 'A': SUB}[p]
        if j in shifts: seq += [()] * shifts[j]
        seq.append(btn(p) if p != '-' else ())
        if j == 74170: seq += [("Left",)] * DL
    return seq
def run(e, seq, verbose=True):
    ev = {}; f = 5225
    def rd():
        m = e.ram(0, 0x800)
        return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], cam=m[0x89] | m[0x8A] << 8,
                    face=any(m[0x3C1+q]==0x60 for q in range(2,15)), lift=[m[0x3FD+q]|m[0x3EE+q]<<8 for q in range(2,15) if m[0x3C1+q]==0x34 and (m[0x439+q]|m[0x42A+q]<<8)==4488],
                    foe=[m[0x51A+q] for q in range(2,15) if m[0x3C1+q]==0x5c])
    for i, b in enumerate(seq):
        e.step(b, 1); f += 1; s = rd()
        if s["hp"] < 47 or s["lives"] < 4: ev["HURT"] = (f, s["x"], s["H"]); break
        if s["foe"] and s["foe"][0] == 0: ev.setdefault("kill", f)
        if s["face"]: ev.setdefault("face", f)
        if s["an"] in (94, 95, 96) and "face" in ev: ev.setdefault("pole", (f, s["x"]))
        if "pole" in ev and s["an"] not in (94, 95, 96): ev.setdefault("drop", f)
        if s["lift"]: ev.setdefault("liftspawn", (f, s["lift"][0], s["x"]))
        if "drop" in ev and s["z"] == 0 and 4486 <= s["H"] <= 4500: ev.setdefault("onlift", f)
        if s["z"] == 0 and s["H"] >= 4570: ev.setdefault("wide", (f, s["x"])); break
    return ev, rd()
if __name__ == "__main__":
    e = BizHawk(log_name="l12f2full.log"); e.load("L12p_f5000")
    for f in range(5000, 5225): e.step(tuple(v for v in ins[f].split('+') if v), 1)
    base = e.msave()
    seq = build({})
    ev, s = run(e, seq)
    print("events:", ev, "end", s, flush=True)
    e.close()
