"""record the base path (c1 rows to 24,200 + legal TAS rows) from 23,663: Ryu X, y, rx, cam, fz, ground flag; + bird 7"""
import sys, json; sys.path.insert(0, 'work/l51c')
from lc import *
F0 = 23663; MST = 'states/mesen/l51c_c1_23663.mst'
rows = c1rows(); hist = rows[:F0]
want = [set(r) for r in rows[F0:24200]] + tasleg(23671, 23800)
cand = enforce(want, hist)
j = 7
fld = dict(FLD); fld.update(vf=0x448+j, vs=0x450+j, xs=0x458+j, bx=0x460+j, by=0x480+j, f4c=0x4C, sf=0x50, ryx=0x86)
fc = F.FastCore(boot_rows=None, ticks=True, fields=fld); fc.put('s', open(MST, 'rb').read()); fc._ka_slot = 's'
r = fc.run_batch('s', [cand], record='all')[0]
o = []
for i, s in enumerate(r.states):
    hi = s['scr_hi']; hi = hi - 256 if hi >= 128 else hi
    v = s['vs']*256 + s['vf']; v = v - 65536 if v >= 32768 else v
    o.append(dict(f=F0+1+i, cam=(hi*256+s['scr_lo'])*256 + s['sf'], X=RXY(s)[0], y=s['y8a'], rx=s['ryx'], fz=s['f4c'] >> 6 & 1,
                  air=s['rf84'] & 4, bx=s['bx'], bs=s['xs'], v=v, by=s['by'], act=s['eact'] >> j & 1, bt=s['t7'], hp=s['hp65'], row=P(cand[i])))
json.dump(o, open('work/l51c/base_path.json', 'w'))
print(len(o), o[-1])
fc.close()
