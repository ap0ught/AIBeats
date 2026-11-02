import sys
sys.path.insert(0, 'work/l32p'); sys.path.insert(0, '.')
from lib import *
k1 = int(sys.argv[1])
fc = core('states/mesen/l31t_tas9828.mst')
rows = TR[9828:k1]
r = fc.run_batch('s', [rows], record='all', stops=[])[0]
bad = None
for i, s in enumerate(r.states):
    t = T[9828 + i + 1]
    if (ax(s), s['y'], s['hp'], s['rng']) != (ax(t), t['y'], t['hp'], t['rng']) and bad is None:
        bad = 9828 + i + 1; print('first diff', bad, ax(s), s['y'], s['hp'], s['rng'], '| TAS', ax(t), t['y'], t['hp'], t['rng'])
s = r.states[-1]; t = T[k1]
print('end', k1, ax(s), s['y'], s['hp'], s['rng'], '| TAS', ax(t), t['y'], t['hp'], t['rng'])
fc.load('s'); fc.step(rows, record='last'); fc.save('e'); fc.save_file('e', f'states/mesen/l32p_tas{k1}.mst', frame=k1); fc.close()
