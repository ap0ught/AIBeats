"""python work/a34r2/mkstate.py <start state> <rows name> <out state>"""
import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_mkstate.log")
try:
    e.load(sys.argv[1]); s = e.run(K.load_rows(sys.argv[2])); e.save(sys.argv[3])
    print(s.frame, s.room, s.x, s.y, hex(s.coll), s.hp)
finally:
    e.close()
