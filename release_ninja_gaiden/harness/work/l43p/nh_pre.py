"""NesHawk check of a 4-3 chain prefix: states/l42a_k18932 + l42_w_k932a_poweron rows 18,933..19,298 + prefix rows;
compare X/y/hp/np/room per frame with the Mesen trace; save NesHawk states at given frames.
python work/l43p/nh_pre.py <prefix rows> <mesen tsv> <save frames comma> <tag>"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
pf, tsv, saves, tag = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')], sys.argv[4]
P = C.rows_of('logs/l42_w_k932a_poweron.inputs.txt')
rows = C.rows_of(pf)
ms = {int(l.split('\t')[0]): tuple(int(v) for v in l.split('\t')[1:]) for l in open(tsv)}
e = C.open_emu('l43p_nhpre.log')
def xy(m):
    hi = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]
    return hi*256 + m[0x51] + m[0x86], m[0x8A]
try:
    e.tick(TICKS)
    st = e.load('l42a_k18932'); print('state', st['frame'], flush=True)
    e.run(P[18932:19298]); print('at 19298', e.state(), flush=True)
    f = 19298; bad = 0
    for k in sorted(set(saves) | {19298 + len(rows)}):
        seg = rows[f - 19298:k - 19298]
        _, rams = e.run_ram(seg)
        for i, m in enumerate(rams):
            g = f + 1 + i
            a = xy(m) + (m[0x65], m[0x64], m[0x6E], m[0xBF])
            if a != ms.get(g):
                bad += 1
                if bad < 60: print('DIFF', g, 'neshawk', a, 'mesen', ms.get(g), 'pad', m[0x2A], flush=True)
        f = k
        if k in saves and rams:
            e.save(f'l43p_{tag}_{k}'); print('saved', f'l43p_{tag}_{k}', xy(rams[-1]), 'hp', rams[-1][0x65], 'np', rams[-1][0x64], 'rm', rams[-1][0x6E], 'BF', rams[-1][0xBF], flush=True)
    print('frames differing', bad, flush=True)
finally:
    e.close()
