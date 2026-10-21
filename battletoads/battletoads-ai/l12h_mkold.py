"""L12h: make a test piece from L12g's own timeline (to develop the later stages before the new upstream exists).
    python l12h_mkold.py <name> <bookmark k (multiple of 250)> <end k> [key=value ...]"""
import sys
from l12h_lib import *
name, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); kw = {x.split("=")[0]: int(x.split("=")[1]) for x in sys.argv[4:]}
G = seg("L12g"); save_piece(name, f"L12h_g_f{a}", a, G[a:b], **kw); print("piece", name, a, b, kw)
