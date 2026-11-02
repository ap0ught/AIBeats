"""Mesen states for 4-3 prep.
(1) TAS: l42p_tas16682.mst + TAS 4-2 pads (tas42_ram.bin) -> 18,960 (= NesHawk ref4751/10_4-3_control), then TAS 4-3 pads
    (tas43_ram.bin) with checkpoints -> states/mesen/l43p_tas<f>.mst
(2) chain: l42a_k18932.mst + l42_w_k932a_poweron rows 18,933..19,298 -> states/mesen/l43p_k932a19298.mst (pre-control)"""
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
g0, p42, _ = pads('work/l42p/tas42_ram.bin')
h0, p43, d43 = pads('work/l43p/tas43_ram.bin')
print('tas42 f0', g0, 'tas43 f0', h0)
fc = F.FastCore(boot_rows=None, ticks=True)
fc.put('s', open('states/mesen/l42p_tas16682.mst', 'rb').read()); fc._ka_slot = 's'; fc.load('s')
fc.step(p42[:18960 - 16682], record='last'); r = fc.ram(); show('mesen tas 18960', r)
fc.save('t'); fc.save_file('t', 'states/mesen/l43p_tas18960.mst', frame=18960); fc._ka_slot = 't'
CK = [19030, 19095, 19160, 19275, 19290, 19330, 19440, 19560, 19640, 19660, 19690, 19725, 19760, 19800, 19830, 20020, 20085,
      20130, 20240, 20400, 20470, 20515, 20570, 20640, 20750, 20820, 20840, 21000, 21060]
f = 18960; ndiff = 0
for ck in CK:
    fc.step(p43[f - 18960:ck - 18960], record='last'); f = ck
    r = fc.ram(); n = d43[(ck - 18961)*2048:(ck - 18960)*2048]
    diff = [hex(a) for a in range(0x800) if r[a] != n[a] and not (0x100 <= a < 0x200)]
    show(f'tas {ck} diffs {len(diff)} {diff[:8]}', r)
    fc.save('c'); fc.save_file('c', f'states/mesen/l43p_tas{ck}.mst', frame=ck)
# chain
P = C.rows_of('logs/l42_w_k932a_poweron.inputs.txt'); print('poweron rows', len(P))
fc.put('k', open('states/mesen/l42a_k18932.mst', 'rb').read()); fc._ka_slot = 'k'; fc.load('k')
fc.step(P[18932:19298], record='last'); r = fc.ram(); show('chain 19298', r)
fc.save('q'); fc.save_file('q', 'states/mesen/l43p_k932a19298.mst', frame=19298); fc._ka_slot = 'q'
fc.step([()], record='last'); r = fc.ram(); show('chain 19299 (blank)', r)
fc.load('q'); fc.step([('Left',)], record='last'); r = fc.ram(); show('chain 19299 (Left)', r)
fc.load('t'); fc.step(p43[:0] or [()], record='last')
fc.close()
