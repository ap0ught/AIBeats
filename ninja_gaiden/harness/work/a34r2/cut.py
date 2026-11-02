"""python work/a34r2/cut.py <start state> <rows> <out rows> <min wpos> : cut the rows at the first frame (after the
prefix start) where Ryu stands on the ground (rflags bit 2 clear, not clinging) with wpos >= min wpos."""
import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_cut.log")
try:
    e.load(sys.argv[1]); rows = K.load_rows(sys.argv[2])
    e.trace(True); e.run(rows); tr = e.last_trace; e.trace(False)
    mw = int(sys.argv[4])
    i = next(i for i, x in enumerate(tr) if K.wpos(x) >= mw and not (x["rflags"] & 4) and not (x["coll"] & 0x2A))
    K.save_rows(sys.argv[3], rows[:i + 1], f"{sys.argv[2]} cut at frame {tr[i]['frame']} wpos {K.wpos(tr[i])} y {tr[i]['y']}")
    print("cut at", tr[i]["frame"], K.wpos(tr[i]), tr[i]["y"], "rows", i + 1)
finally:
    e.close()
