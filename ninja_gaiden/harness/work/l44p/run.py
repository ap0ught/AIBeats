"""Play 4-4 rows (from the control row) then a tail to the 5-1 control; report kill / tally / load / 5-1 control frames.
Frame = power-on row on the TAS axis (control row = 21,353).  Library: fin(fc, rows, start_at=None) with fc at PRE."""
import sys
sys.path.insert(0, 'work/l44p')
from lib import *
CTL0 = 21353

def fin(fc, rows, start_at=None, slot='s', pokes=None, right_from=None, maxf=900):
    """start_at: frame of a 2-f Start (None = keep pressing Start every 6 f from the timer-0 frame (earliest-Start search)).
    right_from: frame from which Right is held (5-1 control test). Returns dict."""
    fc.load(slot)
    for k, v in (pokes or {}).items(): fc.poke(k, v)
    out = dict(kill=None, t_kill=None, np_kill=None, load=None, ctl=None, tally0=None, hp_kill=None)
    f = CTL0 - 1
    i = 0
    st_prev = 11; m = None
    while f < CTL0 + maxf:
        f += 1
        if i < len(rows):
            r = rows[i]
        else:
            r = ()
            if start_at is not None and f in (start_at, start_at + 1): r = ('Start',)
            if right_from is not None and f >= right_from: r = tuple(sorted(set(r) | {'Right'}))
        i += 1
        fc.step([r]); m = fc.ram()
        if out['kill'] is None and m[0x66] == 0 and m[0x6D] == 11:
            out.update(kill=f, t_kill=m[0x63], np_kill=m[0x64], hp_kill=m[0x65], x_kill=m[0x86], y_kill=m[0x8A])
        if out['kill'] and out['tally0'] is None and m[0x63] == 0 and m[0x64] == 0:
            out['tally0'] = f
        if out['load'] is None and m[0x6D] == 12:
            out['load'] = f; t62_load = m[0x62]
        elif out['load'] and m[0x6D] == 12 and m[0x62] != t62_load:
            out['ctl'] = f; out['x_ctl'] = m[0x86]; out['62_ctl'] = m[0x62]; out['BF_ctl'] = m[0xBF]; break
    return out

if __name__ == '__main__':
    src = sys.argv[1]
    rows = [tuple(sorted(r)) for r in C.rows_of(src)]
    sa = int(sys.argv[2]) if len(sys.argv) > 2 else None
    fc = core(PRE)
    print(fin(fc, rows, start_at=sa))
    fc.close()
