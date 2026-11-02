from ng.emulator import LOGS_DIR
rams=[]; sts=[]
rows=[()]*39+[('Start',)]*2+[()]*3600
for i in range(0,len(rows),30):
    s,r=e.run_ram(rows[i:i+30]); sts+=s; rams+=r
    shot(f'cap2/{s[-1].frame:05d}')
np.save(LOGS_DIR/'cap2.ram.npy', np.frombuffer(b''.join(rams),dtype=np.uint8).reshape(-1,2048))
open(LOGS_DIR/'cap2.states.txt','w').write('\n'.join(str(s) for s in sts))
