"""Replay rows from a start state and print every room change (frame, X, y) and the state every --every frames.
    python work/a12r3/rooms.py <start> <rows> [--every 0] [--from F]"""
import sys
sys.path.insert(0, 'ng/stages')
sys.path.insert(0, '.')
import a56_common as C  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402

a = sys.argv[1:]
every = int(a[a.index('--every') + 1]) if '--every' in a else 0
ffrom = int(a[a.index('--from') + 1]) if '--from' in a else 0
rows = [tuple(r) for r in read_inputs(a[1])]
e = C.open_emu('a12r3_probe.log')
try:
    e.tick(TICKS)
    e.load(a[0])
    tr = C.play_trace(e, rows)
    prev = None
    pnp = None
    for i, s in enumerate(tr):
        key = (s.get('stage'), s['room'])
        if key != prev:
            print('ROOM', key, 'frame', s['frame'], 'row', i, C.abs_x(s), s['y'], 'hp', s['hp'], 'np', s['ninpo'],
                  'item', s.get('item'), flush=True)
            prev = key
        if s['ninpo'] != pnp:
            print('  NINPO', s['ninpo'], 'frame', s['frame'], 'row', i, C.abs_x(s), s['y'], 'room', s['room'], 'rows', '+'.join(rows[i]) or '-', '+'.join(rows[i - 1]) if i else '')
            pnp = s['ninpo']
        if every and s['frame'] >= ffrom and i % every == 0:
            print('  ', s['frame'], 'row', i, C.abs_x(s), s['y'], 'r', s['room'], 'hp', s['hp'], 'np', s['ninpo'],
                  '+'.join(rows[i]) or '-', 'D' if s.get('dw') else '')
    print('END', tr[-1]['frame'], C.abs_x(tr[-1]), tr[-1]['y'], 'stage', tr[-1].get('stage'), 'room', tr[-1]['room'],
          'gm', tr[-1].get('gm'))
finally:
    e.close()
