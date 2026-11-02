"""5-2 room-23 legal prefix (legalized TAS rows from the 5-2 control row 24,427) and its arrival independence:
from the Mesen TAS state 24,147 (5-1, before the trigger) poke $BF and junk into the enemy RAM ($400-$4A7, enemy slots), play the TAS
rows to 24,426, then the prefix; compare Ryu with the TAS every frame.  python work/l52p/pre52.py END [--write file]"""
import sys, random
sys.path.insert(0, 'work/l52p')
from lib import *
END = int(sys.argv[1]); WR = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--write' else ''
hist = [tuple(sorted(set(T(f)) - {'Up', 'Down'} - ({'Left'} if {'Left','Right'} <= set(T(f)) else set()))) for f in range(24427 - 150, 24427)]
en = A.Enforcer(hist)
rows = []
for f in range(24427, END + 1):
    w = set(T(f)) - {'Up', 'Down'}
    if {'Left', 'Right'} <= w: w -= {'Right'}
    rows.append(tuple(sorted(en.emit(tuple(sorted(w))))))
print('legal:', legal_ok(rows, hist) or 'ok', 'rows', len(rows))
fc = core('states/mesen/l51p_tas24147.mst'); fc.save('b'); fc._ka_slot = 'b'
pads = [TM(g)[0x2A] for g in range(24148, 24427)]
random.seed(1)
for trial in range(8):
    fc.load('b')
    bf = (trial * 37) % 256
    fc.poke(0xBF, bf)
    if trial:
        for a_ in range(0x400, 0x4A8): fc.poke(a_, random.randrange(256))
    fc.save('t')
    r = fc.run_batch('t', [list(pads) + rows], record='all')[0]
    st = r.states[len(pads):]
    div = None
    for i, s in enumerate(st):
        f = 24427 + i
        if RXY(s) != tas_xy(f) or s['hp65'] != TM(f)[0x65]: div = (f, RXY(s), tas_xy(f)); break
    s = st[-1]
    print(f'trial {trial} BF@24147 {bf} junk {bool(trial)}: first divergence {div}; end {END} X,y {RXY(s)} hp {s["hp65"]} np {s["np64"]}', flush=True)
fc.close()
if WR: open(WR, 'w').write(f'# 5-2 legal prefix: rows 24,427..{END} (row 1 = the 5-2 control row, Left)\n' + '\n'.join(P(r) for r in rows) + '\n')
