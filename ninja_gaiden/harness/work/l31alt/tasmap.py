"""NesHawk: TAS from ref4751/05_3-1_control to frame N; print collision map + lanterns + Ryu (screen coords)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C, hitbox as H
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l31alt_tasmap.log')
try:
    e.tick(TICKS); st = e.load('ref4751/05_3-1_control'); f0 = st['frame']
    for N in map(int, sys.argv[1:]):
        _, rams = e.run_ram(TR[f0:N]); f0 = N; m = rams[-1]
        sc = (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51]
        print('frame', N, 'scroll', sc, 'ryu', H.ryu(m))
        print('lanterns', [(sc + l['x'], l['y'], l) for l in H.lanterns(m)])
        tk = H.tile_kinds(m)
        for r_, line in enumerate(tk): print(r_, ''.join('.' if v == 0 else '%x' % v for v in line))
finally:
    e.close()
