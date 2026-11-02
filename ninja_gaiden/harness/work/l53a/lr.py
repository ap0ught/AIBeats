"""l53a low-RAM runner (coordinator's low-RAM mode: one Mesen at a time, gated at >= 1.5 GB available):
lowers FastCore's own free-RAM floor to 1.5 GB, then runs the script. python work/l53a/lr.py script.py args..."""
import sys, runpy
sys.path.insert(0, '.')
from ng import fastcore as F
f = F.FastCore.__init__
d = list(f.__defaults__); d[-1] = 1.5; f.__defaults__ = tuple(d)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
