"""l62: Mesen state from a power-on file + a Mesen state, with NesHawk conflict frames applied (pad kept from the previous frame);
compares with a NesHawk RAM dump. python work/l62/mkm.py poweron start.mst F0 F1 out.mst [--conf 31840,...] [--nhram file]"""
import sys
sys.path.insert(0, 'work/l62')
from lib62 import *
from ng.inputs import read_inputs
from ng.fastcore import masks_of
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
CF = [int(x) for x in opt('--conf', '').split(',') if x]; NHR = opt('--nhram', '')
rows = read_inputs(a[0]); mst = a[1]; f0 = int(a[2]); f1 = int(a[3]); out = a[4]
m = bytearray(masks_of(list(rows[f0:f1])))
for c in CF: m[c - f0 - 1] = m[c - f0 - 2]
fc = core(mst)
fc.step(bytes(m), record='last')
r = fc.ram(); fc.save('s'); fc.save_file('s', out, f1)
print('after row', f1, 'room', r[0x6E], 'X,y', XY(r), 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'BF', r[0xBF], '$62', r[0x62], '$3E', r[0x3E])
if NHR:
    n = open(NHR, 'rb').read()
    print('diffs vs NesHawk', [(hex(x), r[x], n[x]) for x in range(0x800) if r[x] != n[x] and not 0x100 <= x < 0x200])
fc.close()
