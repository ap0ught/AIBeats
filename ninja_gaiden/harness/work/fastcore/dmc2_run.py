import sys; sys.path.insert(0, 'work/fastcore')
import sync_test as S
tr = S.load_trace('logs/tas4751.trace.csv'); ip = S.NAMES.index('pad')
masks = [tr[k][1][ip] for k in range(1, max(tr) + 1)]
S.run('logs/tas4751.inputs.txt', 'dmc2', 1, 'nes', int(sys.argv[1]), False, force=True, masks=masks, tpl='dmc2_tpl.lua')
