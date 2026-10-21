"""Level 3 Turbo Tunnel skip (speedrun.com Any% allows it): from L3_bikes_seen, mount the bike and roll it back
(TAS #5093's Left+Up taps), dive Left+Down into the pit behind the start line before the first checkpoint saves
$E5/$E6, respawn with the object-list pointer $B7/$B8 = $000B, then follow TAS #5093's post-respawn inputs so the
walk through the object tables reads slot 6's x (= $7F) at $0403 and spawns the level-end object. Writes
logs/pbeam_L3skip.json and bookmark L3skip_end."""
import json
from toads.emulator import BizHawk
from skip3_tas import tas_seq

def conv(b):
    names = ["Right", "Left", "Down", "Up", "Start", "Select", "B", "A"]
    return "+".join(n for n, c in zip(names, b) if c != ".")

def main():
    rows = {}
    for ln in open("tas/ram_skip_1p.txt"):
        f, b, _ = ln.split(); rows[int(f[1:])] = b
    e = BizHawk(log_name="l3skip.log")
    e.load("L3_bikes_seen")
    ins = []
    for b in tas_seq(9):
        r = e.ram_all()
        if (r[0xB7] | r[0xB8] << 8) < 0x800: break
        e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b)
    dive = len(ins)
    print("pointer in RAM after", dive, "frames", flush=True)
    post = [conv(rows[f]) for f in range(14852, 15320)]
    spawn = None
    for k, b in enumerate(post):
        r = e.ram_all()
        if spawn is None and 0x7F in r[0x3C1:0x3D0]: spawn = len(ins); print("0x7F at", spawn, flush=True)
        if r[0x10] != 3:
            break                         # level over: the next segment starts here, like L3t_end
        e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b)
    r = e.ram_all()
    print("end", len(ins), "level", r[0x10], "st", r[0x3B5], "lives", r[0x11], "hp", r[0x51A], "x", r[0x3FD], flush=True)
    e.save("L3skip_end")
    json.dump({"bookmark": "L3_bikes_seen", "inputs": ins,
               "note": "TURBO TUNNEL SKIP. Roll the bike back and drive it into the pit before the first checkpoint saves; the "
                       "respawn reads the level's object list from RAM, and the object tables themselves spawn the level-end "
                       "object.||$B7/$B8 = $000B after the respawn; slot 6's x = $7F is read as an object id at $0403"},
              open("logs/pbeam_L3skip.json", "w"))
    e.close()

if __name__ == "__main__":
    main()
