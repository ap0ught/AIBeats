"""python work/l22c/addspec.py <stage rows in> "<spec>" <out>   append legalized spec rows (on power-on hist) """
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/w21'); sys.path.insert(0,'work/l22f')
from lib import *
from wlib import spec
rows=C.rows_of(sys.argv[1]); add=legal_after(rows, spec(sys.argv[2]))
C.write_inputs(sys.argv[3], rows+add, f'{sys.argv[1]} + {sys.argv[2]}'); print(len(rows+add))
