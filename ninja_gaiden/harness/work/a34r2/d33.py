import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
t4, ja, jd = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
e = K.open_emu("a34r2_d33.log")
try:
    e.load("ref4751/07_3-3_control")
    pre = K.load_rows("b33_pre2")[:13792 - 13741]
    e.run(pre)
    rows = {}
    rows[t4] = ("Up", "B"); rows[t4 + 1] = ("Up", "B")
    for g in range(t4 + 2, ja): rows[g] = ("Right",)
    jr = ("A",) if jd == "A" else ("Right", "A")
    rows[ja] = jr; rows[ja + 1] = jr
    g = ja + 1
    while g < 13930:
        rows[g] = ("Down", "B"); rows[g + 1] = ("Down", "B"); g += 5
    seq = [rows.get(g, ()) for g in range(13793, 13930)]
    leg = K.greedy_legal(seq, K.Legal(pre))
    for i, r in enumerate(leg):
        s = e.step(r, 1)
        rb = e.ram(0x400, 0xC0)
        if s.frame % 2 == 0 or s.boss_real != prev if i else True:
            print(s.frame, "ryu", s.x, s.y, "hp", s.hp, "nin", s.ninpo, "boss", s.boss_real, "bx", rb[0x67], "by", rb[0x87], "+".join(r))
        prev = s.boss_real
finally:
    e.close()
