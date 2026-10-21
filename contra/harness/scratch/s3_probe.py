"""chain2 diagnosis: load stage 3 climb node states and step with no input; print Bill and nearby enemies."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from contra.emulator import BizHawk
F = {"x": 0x334, "y": 0x31A, "pstate": 0x90, "death": 0xB4, "weapon": 0xAA, "fc": 0x1A, "rng": 0x34, "lroutine": 0x2C}
if __name__ == "__main__":
    with BizHawk(log_name="chain/diag_s3.log", fields=F) as e:
        for name in sys.argv[1:]:
            e.load(name)
            print("==", name)
            for k in range(12):
                s = e.step((), 1)
                et = e.ram(0x528, 16); ex = e.ram(0x33E, 16); ey = e.ram(0x324, 16); rt = e.ram(0x4B8, 16)
                ens = [(i, et[i], ex[i], ey[i], rt[i]) for i in range(16) if rt[i]]
                print(k, "bill", s["x"], s["y"], "pstate", s["pstate"], "death", s["death"], "wpn", s["weapon"], "enemies(slot,type,x,y,rt)", ens)
