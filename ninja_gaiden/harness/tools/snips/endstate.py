import sys; sys.path.insert(0,'.')
from ng.inputs import read_inputs
rows=read_inputs('logs/tas4751.inputs.txt')
s=e.load('ref4751/room47_6-5'); f=s.frame; print('room47 state frame', f, s)
s=e.run(rows[f:]); print('end', s)
e.save('ref4751/21_6-5_movie_end'); shot('ref4751/21_6-5_movie_end')
