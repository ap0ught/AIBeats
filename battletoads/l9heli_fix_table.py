"""Print the new Level 9 line around the helicopter shaft as a phase table (input runs with the toad's x, height, speed, animation), and
the objects near it at a few frames.   python l9heli_fix_table.py <tag> <first new index> <last new index>"""
import json, sys
from l9heli_fix_lib import *
TAG, A, B = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ins = up14_inputs(); new = json.load(open(LOGS_DIR / f"pbeam_L9heli_{TAG}.json"))["inputs"]
e = BizHawk(log_name="l9heli_fix_table.log"); base = (OFF + A - 1) // 1000 * 1000
e.load(f"cap14_f{base}")
for i in range(base - OFF, A - 1): e.step(bt(new[i]), 1)
seg = []; prev = None
for i in range(A - 1, B):
    e.step(bt(new[i]), 1); m = e.ram(0, 0x800)
    r = dict(k=i + 1, inp=new[i], x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3D0], spd=m[0x565], hp=m[0x51A], sh=m[0x466], t=m[0x0B])
    key = (r["inp"], r["z"] > 0)
    if key != prev: seg.append([r, r]); prev = key
    else: seg[-1][1] = r
for a, b in seg:
    print(f"{a['k']:5d}-{b['k']:5d} (route frame {a['k'] + OFF}-{b['k'] + OFF}, {b['k'] - a['k'] + 1:3d} f) {a['inp'] or 'nothing':10} {'air' if a['z'] else 'ground':6} x {a['x']}->{b['x']} H {a['H']}->{b['H']} speed {a['spd']}->{b['spd']} anim {a['an']}->{b['an']} hp {b['hp']}", flush=True)
e.close()
