"""Mesen states: (1) TAS 4-2 control 16,682 = l41p_tas14569.mst + TAS 4-1 effective pads -> states/mesen/l42p_tas16682.mst
(2) our c3b 4-2 control 17,020 = l41q_ctl.mst (14,848) + c3b stage rows 2.. -> states/mesen/l42p_c3b17020.mst"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
def pads(fn):
    d = open(fn, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
    return f0, bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048)), d
def show(tag, r):
    X = r[0x52]*256 + r[0x51] + r[0x86]
    print(tag, 'X', X, 'x', r[0x86], 'y', r[0x8A], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF], '62', r[0x62],
          'st', r[0x6D], 'rm', r[0x6E], 'en', hex(r[0x73]), flush=True)
f0, p41, _ = pads('work/l41p/tas41_ram.bin')
g0, p42, d42 = pads('work/l42p/tas42_ram.bin')
fc = F.FastCore(boot_rows=None, ticks=True)
fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
fc.step(p41[:16682 - 14569], record='last'); r = fc.ram(); show('mesen tas 16682', r)
m = d42[:0]  # NesHawk at 16682 is the frame before the dump start; compare at 16683 instead
fc.save('t'); fc.save_file('t', 'states/mesen/l42p_tas16682.mst', frame=16682)
fc.step(p42[:1], record='last'); r = fc.ram(); show('mesen tas 16683', r)
n = d42[0:2048]; show('neshawk 16683', n)
diff = [hex(a) for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
print('diff vs NesHawk at 16683 (excl stack):', diff[:40], flush=True)
# our chain
S = C.rows_of('logs/l41_c3b.inputs.txt'); print('c3b rows', len(S), S[:2], S[-3:])
fc.put('q', open('states/mesen/l41q_ctl.mst', 'rb').read()); fc._ka_slot = 'q'; fc.load('q')
fc.step(S[1:], record='last'); r = fc.ram(); show('mesen c3b at 14848+%d' % (len(S) - 1), r)
fc.save('c'); fc.save_file('c', 'states/mesen/l42p_c3b17020.mst', frame=14848 + len(S) - 1)
t = open('states/mesen/l42p_tas16682.mst', 'rb').read()
fc.put('t2', t); fc.load('t2'); rt = fc.ram()
diff = [hex(a) for a in range(0x800) if r[a] != rt[a] and not (0x100 <= a < 0x200)]
print('our 4-2 control vs TAS 4-2 control RAM diffs:', diff, flush=True)
print([(a, r[int(a, 16)], rt[int(a, 16)]) for a in diff][:60])
fc.close()
