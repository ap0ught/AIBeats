import sys
sys.path.insert(0, '.')
from ng.solve import common as C
e = C.open_emu("c5_slots_emu.log")
try:
    for st in sys.argv[1].split(","):
        e.load(st)
        print("==", st)
        for k in range(int(sys.argv[2])):
            r = e.ram_all()
            if k % int(sys.argv[3]) == 0:
                print(k, " ".join(f"{r[0x400+i]:02x}:{r[0x460+i]:3d},{r[0x480+i]:3d},{r[0x490+i]:2d}" for i in range(8)), "ryu", r[0x86], r[0x8A], "hp", r[0x65], "66=", r[0x66])
            e.run([()])
finally:
    e.close()
