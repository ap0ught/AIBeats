"""Extend 1-frame Left holds at 26,506 (room-26 change; inputs ignored there) in a power-on file. python work/l52b/fixhold.py file"""
import sys; sys.path.insert(0,'.')
from ng.inputs import read_inputs, write_inputs
p = sys.argv[1]; r = [tuple(x) for x in read_inputs(p)]
if r[26505] == ('Left',) and r[26506] == () and r[26504] != ('Left',): r[26506] = ('Left',)
write_inputs(p, r, 'power-on: l52a d3 rows 1-25,495 (locked 1-24,997) + l52b rooms 24-26; last row = 5-3 control (Left)')
print(len(r))
