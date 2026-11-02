"""4-1c entry probe: run b41_pre2, wait to the room-15 control, walk right to the wall, save cling state."""
import sys
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
e = K.open_emu("a34r2_x41c.log")
try:
    e.load("ref4751/08_4-1_control")
    pre = K.load_rows("b41_pre2")
    s = e.run(pre)
    print("after pre", s.frame, s.room, s.x, s.y, hex(s.coll), "hp", s.hp)
    rows = list(pre)
    for i in range(60):
        s = e.step((), 1); rows.append(())
        print(s.frame, s.room, "x", s.x, "y", s.y, hex(s.coll), s.rflags, K.wpos(s))
        if s.room == 15 and s.y >= 200 and not (s.rflags & 4):
            break
    e.screenshot("tmp/a34r2_x/e41c_entry")
    K.save_rows("r2_41c_entry", rows, "b41_pre2 + wait to the room-15 floor")
    e.save("tmp/a34r2_x/e41c_entry")
    for i in range(40):
        s = e.step(("Right",), 1); rows.append(("Right",))
        print(s.frame, "x", s.x, "y", s.y, hex(s.coll), s.rflags, K.wpos(s))
        if s.coll & 0x2A and i > 2:
            break
    e.screenshot("tmp/a34r2_x/e41c_wall")
    e.save("tmp/a34r2_x/e41c_wall")
    K.save_rows("r2_41c_wall", rows, "to the wall")
finally:
    e.close()
