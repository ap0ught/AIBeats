"""record Ryu + bird slot j per frame: python work/l51c/rec.py mst F0 F1 j out.json [rowsfile]"""
import sys, json; sys.path.insert(0, 'work/l51c')
from lc import *
mst, F0, F1, j, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
rows = [tuple(sorted(r)) for r in C.rows_of(sys.argv[6])] if len(sys.argv) > 6 else c1rows()
fld = dict(FLD); fld.update(vf=0x448+j, vs=0x450+j, xs=0x458+j, bx=0x460+j, by=0x480+j, f4c=0x4C, sf=0x50, bt=0x400+j, ryx=0x86)
fc = F.FastCore(boot_rows=None, ticks=True, fields=fld); fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'
r = fc.run_batch('s', [rows[F0:F1]], record='all')[0]
o = []
for i, s in enumerate(r.states):
    hi = s['scr_hi']; hi = hi - 256 if hi >= 128 else hi
    v = s['vs']*256 + s['vf']; v = v - 65536 if v >= 32768 else v
    o.append(dict(f=F0+1+i, scr=hi*256+s['scr_lo'], X=RXY(s)[0], y=s['y8a'], rx=s['ryx'], fz=s['f4c'] >> 6 & 1,
                  bt=s['bt'], bx=s['bx'], bs=s['xs'], v=v, by=s['by'], act=s['eact'] >> j & 1, hp=s['hp65']))
json.dump(o, open(out, 'w'))
fc.close()
