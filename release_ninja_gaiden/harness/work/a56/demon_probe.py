import sys
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); T = C.tas_trace(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/room47_6-5'); f = s.frame
        e.run([()] * 151); f += 151
        hist = C.legalize(R[f - 1900:f])
        rows = C.legalize(R[f:39090], history=hist)
        tr = C.play_trace(e, rows)
        for t, r in zip(tr, rows):
            if t['frame'] >= 39040 and t['frame'] % 2 == 0 or t['bosshp'] != 16:
                tt = T[min(t['frame'], 39084)]
                print(t['frame'], '+'.join(r), C.abs_x(t), t['y'], 'bh', t['bosshp'], 'real', t['boss_real'], '| TAS', '+'.join(R[t['frame']-1]), C.abs_x(tt), tt['y'], tt['bosshp'])
                if t['frame'] > 39120: break
    finally:
        e.close()
