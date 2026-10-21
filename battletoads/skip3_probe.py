"""Probe the Turbo Tunnel skip: from the bike mount, steer Left+Down into the pit (TAS #5093 does this ~35 frames
after mounting) and watch the object-list pointer $B7/$B8 and the checkpoint pointer $E5/$E6 through the respawn."""
import sys
from toads.emulator import BizHawk

def row(e, k, b):
    r = e.ram_all()
    return (f"k{k:4d} {b:10s} B7/B8 {r[0xB7]:3d}/{r[0xB8]:3d} E5/E6 {r[0xE5]}/{r[0xE6]} cam {r[0x87]|r[0x88]<<8:5d} "
            f"x {r[0x3FD]:3d} y {r[0x41B]:3d} h {r[0x439]:3d} z {r[0x475]:3d} st {r[0x3B5]:3d} D5 {r[0xD5]} hp {r[0x51A]:2d} "
            f"lives {r[0x11]} 0B {r[0x0B]:3d} 0C {r[0x0C]:3d} ids {[r[0x3C1+i] for i in range(8)]}")

def main():
    delay = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    btn = sys.argv[2] if len(sys.argv) > 2 else "Left+Down"
    e = BizHawk(log_name="skip3_probe.log")
    e.load("L3_bike_go")
    print(row(e, 0, "start"))
    for k in range(1, 400):
        b = "Left" if k <= delay else btn
        e.step(tuple(x for x in b.split("+") if x), 1)
        r = e.ram_all()
        if k % 10 == 0 or r[0x51A] == 0 or (r[0xB7] | r[0xB8] << 8) < 0x800:
            print(row(e, k, b))
        if (r[0xB7] | r[0xB8] << 8) < 0x800 and k > 5:
            break
    e.save("L3_skip_respawn")
    e.close()

if __name__ == "__main__":
    main()
