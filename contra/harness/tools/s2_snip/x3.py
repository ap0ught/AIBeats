import time
e.mload(G["s2_0"])
e.trace(False)
t=time.time(); 
for _ in range(300): e.step((),1)
t1=time.time()-t
ids=[]
t=time.time()
for _ in range(200): ids.append(e.msave())
t2=time.time()-t
t=time.time()
for k in ids: e.mload(k)
t3=time.time()-t
t=time.time()
for k in ids: e.cmd(f"mload {k}"); e.cmd("stepx 00")
t4=time.time()-t
for k in ids: e.mfree(k)
t=time.time(); e.step((),2000); t5=time.time()-t
e.trace(True); t=time.time(); e.step((),1000); t6=time.time()-t
print(f"step1 x300 {t1:.2f}s  msave x200 {t2:.2f}s  mload(with state) x200 {t3:.2f}s  mload+step x200 {t4:.2f}s  2000 frames {t5:.2f}s  1000 traced {t6:.2f}s fields {len(e.fields)}")
