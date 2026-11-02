"""base path for another climb: rows = pre (power-on rows to CUT) + c1 rows from R0 to 24,200 + legal TAS rows from 23,671.
The wall bird (slot 7) is removed after CUT (poke) so the recorded Ryu path has no bird hits; its state at CUT is the sim's start.
python work/l51c/recbase2.py <prefix power-on rows file> <base mst> <mst frame> CUT R0 out.json"""
import sys, json; sys.path.insert(0, 'work/l51c')
from lc import *
pref, mst, MF, CUT, R0, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
pre = [tuple(sorted(r)) for r in C.rows_of(pref)]
c1 = c1rows()
j = 7
fld = dict(FLD); fld.update(vf=0x448+j, vs=0x450+j, xs=0x458+j, bx=0x460+j, by=0x480+j, f4c=0x4C, sf=0x50, ryx=0x86)
fc = F.FastCore(boot_rows=None, ticks=True, fields=fld); fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'
r = fc.run_batch('s', [pre[MF:CUT]], record='last', keep=True, prefix='o')[0]
s = r.states[-1]; hi = s['scr_hi']; hi = hi - 256 if hi >= 128 else hi
v = s['vs']*256 + s['vf']; v = v - 65536 if v >= 32768 else v
bird = dict(B=((hi*256 + s['scr_lo'])*256 + s['sf']) + s['bx']*256 + s['xs'], V=v, Y=s['by'], t=s['t7'], act=s['eact'] >> 7 & 1)
print('bird at', CUT, bird, line(CUT, s))
fc.load('o1'); ram = fc.ram(); fc.poke(0x73, ram[0x73] & 0x7F); fc.poke(0x400 + j, 0); fc.save('n'); fc._ka_slot = 'n'
hist = pre[:CUT]
want = [set(x) for x in c1[R0:24200]] + tasleg(23671, 23800)
cand = enforce(want, hist)
rr = fc.run_batch('n', [cand], record='all')[0]
o = []
for i, s in enumerate(rr.states):
    hi = s['scr_hi']; hi = hi - 256 if hi >= 128 else hi
    o.append(dict(f=CUT+1+i, cam=(hi*256+s['scr_lo'])*256 + s['sf'], X=RXY(s)[0], y=s['y8a'], rx=s['ryx'], fz=s['f4c'] >> 6 & 1,
                  air=s['rf84'] & 4, hp=s['hp65'], row=P(cand[i]), act=s['eact'] >> 7 & 1, bt=s['t7']))
json.dump(dict(bird=bird, cut=CUT, r0=R0, path=o, rows=[P(x) for x in cand]), open(out, 'w'))
print('recorded', len(o), 'hp changes', [(a['f'], a['hp']) for k, a in enumerate(o) if k and a['hp'] != o[k-1]['hp']][:5], 'slot7 reused', [a['f'] for a in o if a['act']][:3])
fc.close()
