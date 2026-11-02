import sys, time
sys.path.insert(0, 'ng/stages')
import a56_common as C
if __name__ == "__main__":
    R = C.tas_rows(); e = C.open_emu("a56_probe.log")
    try:
        s = e.load('ref4751/16_6-1_control'); f = s.frame
        for fs in (0, 9, 0):
            e.frameskip(fs)
            e.load('ref4751/16_6-1_control')
            t = time.time(); e.run(R[f:f+600]); dt = time.time() - t
            print('frameskip', fs, 'fps', 600/dt)
        sid = e.msave()
        t = time.time()
        for i in range(50):
            e.mload(sid); e.run(R[f:f+8]); x = e.ram_all(); s2 = e.msave(); e.mfree(s2)
        dt = time.time() - t; print('eval8 per s', 50/dt)
        t = time.time()
        for i in range(50):
            e.mload(sid)
        print('mload per s', 50/(time.time()-t))
        t = time.time()
        for i in range(50):
            x = e.ram_all()
        print('ram per s', 50/(time.time()-t))
        t = time.time()
        for i in range(50):
            s2 = e.msave(); e.mfree(s2)
        print('msave+free per s', 50/(time.time()-t))
    finally:
        e.close()
