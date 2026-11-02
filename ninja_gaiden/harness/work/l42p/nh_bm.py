"""NesHawk check of a window-2 beam file: python work/l42p/nh_bm.py <c> [c ...]  (bm_w2_<c>.inputs.txt)"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
CTL = '--ctl' in sys.argv
if CTL: sys.argv.remove('--ctl')
e = C.open_emu('l42p_nhbm.log')
try:
    e.tick(TICKS)
    for c in sys.argv[1:]:
        rows = C.rows_of(f'work/l42p/bm_w2_{c}.inputs.txt')
        st = e.load('ref4751/09_4-2_control')
        if CTL:
            e.poke(0xBF, int(c)); K = 0
        else:
            e.run(rows[:17355 - 16681]); e.poke(0xBF, (int(c) + 673) & 255); K = 17355 - 16681
        out = []
        hp = 16; xs = {}
        for i, r in enumerate(rows[K:]):
            s = e.step(r)
            if s['hp'] < hp: out.append(('hit', s['frame'], s['hp']))
            if s['frame'] in (17440, 17500, 17550, 17605): xs[s['frame']] = (s['x'], s['y'])
            hp = s['hp']
        s = e.state()
        X = s['x'] + (s['scroll'] if 'scroll' in s else 0)
        print('c', c, 'poke at control' if CTL else 'poke at 17355', xs, 'end frame', s['frame'], 'x', s['x'], 'scroll', s.get('scroll'), 'scr', s.get('scroll_scr'), 'y', s['y'], 'hp', s['hp'], 'np', s['ninpo'], out, flush=True)
finally:
    e.close()
