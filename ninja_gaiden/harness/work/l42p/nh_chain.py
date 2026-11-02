"""NesHawk on the locked chain: lock_41q_pre (14,847) + r15_c power-on rows 14,848-16,997 + 4-2 stage rows (row 1 = the
control row 16,998). Compares with the TAS dump at TAS frame = frame - 316; lists misreads, hits; saves a state at the end.
python work/l42p/nh_chain.py <stage rows> <save name>"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
from ng.inputs import to_mask
DBGF = set(range(17068, 17080))
P = C.rows_of('logs/l41_r15_c_poweron.inputs.txt'); R = [tuple(r) for r in C.rows_of(sys.argv[1])]
d = open('work/l42p/tas42_ram.bin', 'rb').read()[4:]
e = C.open_emu('l42p_nhchain.log')
try:
    e.tick(TICKS); st = e.load('lock_41q_pre'); print('pre', st['frame'])
    e.run(P[14847:16997]); s = e.state(); print('16997', s['frame'], 'x', s['x'], 'BF', s['rng'])
    _, rams = e.run_ram(R)
    e.save(sys.argv[2])
finally:
    e.close()
mis = []; hp = 16; div = None; ndiff = 0; last = None
for i, m in enumerate(rams):
    f = 16998 + i; tf = f - 316
    if m[0x2A] != to_mask(R[i]): mis.append(f)
    if f in DBGF: print(f, 'row', R[i], 'pad', m[0x2A], 'X', m[0x52]*256 + m[0x51] + m[0x86], 'y', m[0x8A])
    t = d[(tf - 16683)*2048:(tf - 16682)*2048] if tf >= 16683 else None
    if t is None: continue
    X = m[0x52]*256 + m[0x51] + m[0x86]; tX = t[0x52]*256 + t[0x51] + t[0x86]
    if (X, m[0x8A]) != (tX, t[0x8A]):
        ndiff += 1; last = (f, X, m[0x8A], tX, t[0x8A])
        if div is None: div = (f, tf, X, m[0x8A], tX, t[0x8A])
    if m[0x65] < hp: print('hit', f, m[0x65], 'X', X)
    hp = m[0x65]
m = rams[-1]
print('end frame', 16997 + len(rams), 'X', X, 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'item', m[0xC9], 'BF', m[0xBF], 'misreads', mis[:10], 'first divergence', div, 'n diff frames', ndiff, 'last diff', last)
