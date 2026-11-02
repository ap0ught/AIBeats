import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/room46_6-4b'); f = s.frame
        e.run(R[f:38132]); sid = e.msave()
        X = [(), ('Up',), ('Down',), ('Left',), ('Right',), ('Up','Left'), ('Up','Right'), ('Down','Left'), ('Down','Right'), ('A',)]
        for x in X:
            for hold_first_down in (True, False):
                e.mload(sid)
                first = ('Down','B') if hold_first_down else ('B',)
                rows = [first, tuple(sorted(set(x) | {'B'})), x, x, first, tuple(sorted(set(x) | {'B'})), x, x, first, x]
                out = []
                for r in rows:
                    e.step(r, 1)
                    m = e.ram(0x80, 4); b = e.ram(0x497, 1)[0]
                    out.append(f'{m[0]:02x}{m[1]:02x}{m[2]:02x}{m[3]:02x}/{b}')
                print(f'{"+".join(first):6s} then {"+".join(x) or "none":11s}', ' '.join(out))
    finally:
        e.close()
