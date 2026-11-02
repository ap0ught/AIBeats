"""NesHawk: load states/lock_32_ctl (11,595), play 3-2 stage rows, print events + X goal frame; optionally save end state.
python work/l32a/nhplay.py <rows file> [--n rows] [--x 1252] [--save name] [--state lock_32_ctl]"""
import sys
sys.path.insert(0, '.')
from ng.solve import common as C
from ng.mode import TICKS
sys.path.insert(0, 'ng/stages')
import a56_common as A
TT = A.tas_trace()
a = sys.argv[1:]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
n = opt('--n', -1); LAG = opt('--lag', 0); EV = opt('--every', 20); FROM = opt('--from', 0); GX = opt('--x', 1252); sv = opt('--save', ''); stn = opt('--state', 'lock_32_ctl')
rows = C.rows_of(a[0]); rows = rows if n < 0 else rows[:n]
e = C.open_emu('l32a_nh.log')
try:
    e.tick(TICKS)
    st = e.load(stn); f0 = st['frame']; print('loaded', stn, 'frame', f0, 'x', st['x'], 'rng', st['rng'])
    sts, rams = e.run_ram(rows)
    got = None; prev = None
    for i, m in enumerate(rams):
        f = f0 + i + 1; X = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51] + m[0x86]
        k = (m[0x64], m[0xC9], m[0x65], m[0xC8])
        if prev is not None and k != prev: print(f, 'row', i + 1, 'X', X, 'y', m[0x8A], 'np', m[0x64], 'it', m[0xC9], 'hp', m[0x65], 'thrown', m[0xC8])
        prev = k
        if LAG and i + 1 >= FROM and (i + 1) % EV == 0:
            t = TT[f - LAG]; sc = X - m[0x86]; print(f, 'row', i + 1, 'X', X, 'y', m[0x8A], 'hp', m[0x65], '| TAS X', C.abs_x(t), 'y', t['y'], 'd', C.abs_x(t) - X, [(m[0x400+j], sc + m[0x460+j], m[0x480+j]) for j in range(8) if m[0x73] >> j & 1])
        if got is None and X >= GX: got = f; print('X>=%d at frame %d row %d y %d hp %d' % (GX, f, i + 1, m[0x8A], m[0x65]))
        if m[0x6D] != 6: print('STAGE CHANGE frame', f, 'row', i + 1); break
    m = rams[-1]; X = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51] + m[0x86]
    print('END frame', f0 + len(rams), 'X', X, 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'bf', m[0xBF], '62', m[0x62])
    if sv: e.save(sv); print('saved', sv)
finally:
    e.close()
