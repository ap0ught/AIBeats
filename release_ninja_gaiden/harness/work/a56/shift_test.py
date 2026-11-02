import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
from ng.mode import TICKS
KEYS = ('x', 'xsub', 'y', 'room', 'scroll', 'scroll_scr', 'hp', 'ninpo')
def run(e, st, rows, shift, f0, n):
    e.load(st)
    tr = C.play_trace(e, rows[:n])
    T = C.tas_trace()
    first = None
    for s in tr:
        t = T[s['frame'] + shift]
        if any(s[k] != t[k] for k in KEYS):
            first = s['frame']; break
    return first, tr
if __name__ == "__main__":
    stage = int(sys.argv[1]); st = sys.argv[2]; n = int(sys.argv[3])
    R = C.tas_rows(); e = C.open_emu("a56_shift.log")
    try:
        s0 = e.load(st); f0 = s0['frame']
        hist = C.legalize(R[f0 - 120:f0])[-60:]
        for shift in (-1, 0, 1, 2):
            # our frame f plays TAS row of frame f+shift
            want = [R[f0 + i + shift] for i in range(n)]   # R[f-1] is frame f; our first frame f0+1 -> TAS frame f0+1+shift
            rows = C.legalize(want, history=hist)
            first, tr = run(e, st, rows, shift, f0, n)
            print('shift', shift, 'in sync until', first, 'last', {k: tr[-1][k] for k in ('frame', 'room', 'x', 'y', 'hp', 'ninpo')})
    finally:
        e.close()
