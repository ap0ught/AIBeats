"""python work/a34r2/shot.py <state> <rows name|-> <extra TAS frames to f|-> <out shot>"""
import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_shot.log")
try:
    s = e.load(sys.argv[1])
    if sys.argv[2] != "-":
        s = e.run(K.load_rows(sys.argv[2]))
    if sys.argv[3] != "-":
        f = int(sys.argv[3]); T = K.tas_rows(); s = e.run(T[s.frame:f])
    e.screenshot(sys.argv[4]); print(s.frame, s.x, s.y, K.wpos(s), s.hp)
finally:
    e.close()
