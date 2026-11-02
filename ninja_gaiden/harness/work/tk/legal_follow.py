"""Play the legalized TAS rows of a stage from a state (ours or the TAS's) and report boss HP / stage end.
    python work/tk/legal_follow.py <state> <hist|-> <tas_k0> <n> [--shift s]
tas_k0 = TAS frame whose state equals ours (rows TAS[k0 .. k0+n-1] are played, legalized against hist)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C, legality as L
from ng.mode import TICKS
import a56_common as A
st, hf, k0, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
hist = C.rows_of(hf) if hf != '-' else []
rows = L.legalize(A.tas_rows()[k0:k0 + n], hist[-1900:])
T = A.tas_trace()
e = C.open_emu('tk_follow.log')
try:
    e.tick(TICKS); s0 = e.load(st); tr = A.play_trace(e, rows)
finally:
    e.close()
for i, s in enumerate(tr):
    t = T[k0 + i + 1]
    if i % 10 == 0 or s['bosshp'] == 0:
        print(i, s['frame'], 'X', C.abs_x(s), s['y'], 'hp', s['hp'], 'np', s['ninpo'], 'boss', s['bosshp'], '| TAS X', C.abs_x(t), t['y'], 'boss', t['bosshp'])
    if s['bosshp'] == 0 and i > 5:
        print('BOSS 0 at row', i); break
C.write_inputs('states/tmp/tk_follow_last.inputs.txt', rows, f'legalized TAS from {k0}')
