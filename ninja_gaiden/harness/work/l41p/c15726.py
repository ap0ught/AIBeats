"""r2c relies on a NesHawk input conflict at 15726 (Left+A effective only on 15727). Test legal 2-frame versions (Mesen, pads)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; pads = bytearray(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
S = 15700
fc.run_batch('s', [bytes(pads[:S - 14569])], record='last', keep=True, prefix='k'); fc._ka_slot = 'k1'
LA = 130
def var(frames, extra=None):
    p = bytearray(pads[S - 14569:])
    for f in range(15725, 15731): p[f - S - 1] = 0
    for f in frames: p[f - S - 1] = LA
    return bytes(p)
V = {'orig(1f 15727)': [15727], 'rows 15726-27': [15726, 15727], '15727-28': [15727, 15728], '15725-26': [15725, 15726], '15728-29': [15728, 15729]}
for name, fr in V.items():
    st = fc.run_batch('k1', [var(fr)], record='all', stops=[(0x6D, 'changed', 0)])[0].states
    r15 = next((S + 1 + i for i, s in enumerate(st) if s['room'] == 15), None)
    print(name, 'end', S + len(st), 'room15', r15, 'stage', st[-1]['stage'], 'hp', st[-1]['hp'], 'y', st[-1]['y'], flush=True)
fc.close()
