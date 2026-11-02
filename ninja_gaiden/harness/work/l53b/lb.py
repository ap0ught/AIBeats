"""l53b: lib (work/l53p) + lower fastcore RAM floor (env MINGB, default 1.5 GB; the owner's rule: one Mesen at >= 1.5 GB)."""
import os, sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lib import *
import fcka as _fk
_d = list(_fk._init.__defaults__); _d[-1] = float(os.environ.get('MINGB', '1.5')); _fk._init.__defaults__ = tuple(_d)
