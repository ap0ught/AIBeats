import sys, time
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    stg = int(sys.argv[1]); st_name = sys.argv[2]
    ev = C.tas_stage(stg); nxt = C.tas_stage(stg+1) if stg < 21 else None
    a = ev['control']; b = (nxt['control'] if nxt else 39084)
    T = C.tas_trace(); R = C.tas_rows()
    e = C.open_emu(f"a56_exp_{stg}.log")
    try:
        s = e.load(st_name); print('loaded frame', s.frame, 'stage', s.stage, 'x', s.x, 'tas x', T[s.frame]['x'])
        f0 = s.frame
        hist = R[f0-60:f0]
        for mode in ('tas', 'legal'):
            e.load(st_name)
            rows = R[f0:b + 50]
            if mode == 'legal': rows = C.legalize(rows, history=C.legalize(hist))
            t0 = time.time(); tr = C.play_trace(e, rows); dt = time.time() - t0
            div = None
            for st in tr:
                t = T[st['frame']]
                if (st['x'], st['y'], st['room'], st['scroll']) != (t['x'], t['y'], t['room'], t['scroll']):
                    div = st['frame']; break
            end = next((st['frame'] for st in tr if st['stage'] != stg), None)
            print(mode, 'fps %.0f' % (len(tr)/dt), 'first divergence', div, 'stage end', end, 'tas end', nxt['load'] if nxt else None,
                  'last', {k: tr[-1][k] for k in ('frame','stage','room','x','y','hp','lives')})
            if div:
                for st in tr:
                    if div - 3 <= st['frame'] <= div + 30 and st['frame'] % 3 == 0:
                        t = T[st['frame']]
                        print('   ', st['frame'], (st['room'], C.abs_x(st), st['y'], st['hp']), 'tas', (t['room'], C.abs_x(t), t['y'], t['hp']), R[st['frame']-1], rows[st['frame']-f0-1])
    finally:
        e.close()
