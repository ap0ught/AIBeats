"""write the head-start stage rows (row 1 = 5-1 control row): D rows to 22,284, Left x2 sink 22,289-90, jump A 22,357-58,
up on the pillar 22,388, then legalized TAS rows from 22,390 at lag -1 (TAS row t -> our frame t-1+DL) to frame END."""
import sys
sys.path.insert(0, 'work/l51p')
import importlib.util
spec = importlib.util.spec_from_file_location('g', 'work/l51p/gate2.py')
src = open('work/l51p/gate2.py').read().split('fc = core(')[0]
g = {}; exec(compile(src, 'gate2', 'exec'), g)
END = int(sys.argv[1]) if len(sys.argv) > 1 else 22490
rows = g['pre'] + g['cont'](g['cand']('Left2@22289', 22357), 22388, 1)
rows = rows[:END - 22124]
print('legal:', g['legal_ok'](rows, [()] * 60) or 'ok', len(rows))
with open(f'work/l51p/pre51_{END}.txt', 'w') as fo:
    fo.write(f'# 5-1 head start: stage rows from the control row 22,125 (TAS axis) to frame {END}; blank control row, Right, Left x2 sink 22,289, boost jump 22,357\n')
    for r in rows: fo.write('+'.join(sorted(r)) + '\n')
