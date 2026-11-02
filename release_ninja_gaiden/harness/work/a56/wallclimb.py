import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
PAT = {
 'LA_R': [('Left','A'),('Left','A'),('Right',),('Right',),()],
 'A_R': [('A',),('A',),('Right',),('Right',),()],
 'RA': [('Right','A'),('Right','A'),('Right',),('Right',),('Right',)],
 'LA_RR': [('Left','A'),('Left','A'),('Right',),('Right',),('Right',)],
 'LA_R6': [('Left','A'),('Left','A'),('Right',),('Right',),(),()],
 'A__R': [('A',),('A',),(),('Right',),('Right',)],
}
if __name__ == "__main__":
    start = int(sys.argv[1]); state = sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load(state); f = s.frame
        e.run(R[f:start]); sid = e.msave()
        s = e.state(); print('at', start, C.abs_x(s), s['y'], 'anim', s['anim'], 'rf', s['rflags'])
        for name, p in PAT.items():
            e.mload(sid)
            rows = (p * 20)[:n]
            tr = C.play_trace(e, rows)
            print(f'{name:6s}', [(C.abs_x(t), t['y']) for t in tr[::3]][:14])
        e.mload(sid)
        tr = C.play_trace(e, R[start:start+n])
        print('TAS   ', [(C.abs_x(t), t['y']) for t in tr[::3]][:14])
    finally:
        e.close()
