import sys, time; sys.path.insert(0, '.')
from ng.fastcore import FastPool, FastCore
from ng.inputs import read_inputs, to_mask
rows = [to_mask(r) for r in read_inputs('logs/a12r3_to22.inputs.txt')]
cands = [rows[174:174 + 300]] * 40
with FastPool(2, boot_rows=rows[:174], ticks=False) as p:
    p.save_all('s')
    t = time.time(); res = p.run_batch('s', cands, record='last'); dt = time.time() - t
    print('pool of 2: %d frames in %.1fs = %.0f f/s; all equal: %s' % (40 * 300, dt, 40 * 300 / dt, len({(r.rows_played, tuple(r.states[-1].items())) for r in res}) == 1))
