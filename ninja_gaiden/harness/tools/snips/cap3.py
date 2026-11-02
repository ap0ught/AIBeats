from ng.emulator import LOGS_DIR
rams=[]; sts=[]
rows=[('Start',)]*2+[()]*38+[('Start',)]*2+[()]*1500
for i in range(0,len(rows),20):
    s,r=e.run_ram(rows[i:i+20]); sts+=s; rams+=r
    shot(f'cap3/{s[-1].frame:05d}')
e.save('cap3_end')
np.save(LOGS_DIR/'cap3.ram.npy', np.frombuffer(b''.join(rams),dtype=np.uint8).reshape(-1,2048))
open(LOGS_DIR/'cap3.states.txt','w').write('\n'.join(str(s) for s in sts))
