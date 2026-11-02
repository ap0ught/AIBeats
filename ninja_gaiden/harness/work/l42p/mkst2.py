"""Mesen state of the LOCKED 4-1 (r15_c): 4-2 control 16,998. l41q_ctl.mst (14,848) + l41_r15_c16844 rows 2.. up to 16,997
-> states/mesen/l42p_lock16997.mst (pre-control), then Right on 16,998 -> l42p_lock16998R.mst. Compare with the TAS state."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
S = C.rows_of('logs/l41_r15_c16844.inputs.txt'); P = C.rows_of('logs/l41_r15_c_poweron.inputs.txt')
print('stage rows', len(S), 'poweron', len(P), 'match', list(P[14847:]) == list(S))
fc = F.FastCore(boot_rows=None, ticks=True)
fc.put('q', open('states/mesen/l41q_ctl.mst', 'rb').read()); fc._ka_slot = 'q'; fc.load('q')
fc.step(S[1:-1], record='last'); r = fc.ram(); fc.save('p'); fc.save_file('p', 'states/mesen/l42p_lock16997.mst', frame=16997)
print('16997 x', r[0x86], 'y', r[0x8A], 'BF', r[0xBF], 'st', r[0x6D], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9])
fc.step([('Right',)], record='last'); r = fc.ram(); fc.save('c'); fc.save_file('c', 'states/mesen/l42p_lock16998R.mst', frame=16998)
print('16998 (Right) x', r[0x86], r[0x85], 'y', r[0x8A], 'BF', r[0xBF], '62', r[0x62])
fc.put('t', open('states/mesen/l42p_tas16682.mst', 'rb').read()); fc.load('t'); rt = fc.ram()
diff = [(hex(a), r[a], rt[a]) for a in range(0x800) if r[a] != rt[a] and not (0x100 <= a < 0x300)]
print('vs TAS 16682 (excl stack/OAM):', diff)
fc.close()
