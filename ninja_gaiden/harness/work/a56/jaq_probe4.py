import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/room46_6-4b'); f = s.frame
        e.run(R[f:38132]); sid = e.msave()
        for name, rows in [('TAS', R[38132:38150]),
                           ('B5', [('Down','B') if i % 5 in (0, 1) else ('Down',) for i in range(18)]),
                           ('B3', [('Down','B') if i % 3 in (0,) else ('Down',) for i in range(18)]),
                           ('B4', [('Down','B') if i % 4 in (0,1) else ('Down',) for i in range(18)])]:
            e.mload(sid)
            out = []
            for r in rows:
                e.step(r, 1)
                m = e.ram(0x80, 4); b = e.ram(0x497, 1)[0]
                out.append(f'{"+".join(r)[:6]:6s} a{m[0]:02x} {m[1]:02x} {m[2]:02x} {m[3]:02x} r{b}')
            print(name); print('   ' + ' | '.join(out[:9])); print('   ' + ' | '.join(out[9:]))
    finally:
        e.close()
