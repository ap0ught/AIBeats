import sys, json
sys.path.insert(0,'.')
from check_inputs import check, read_rows
rows,_ = read_rows('logs/tas4751.inputs.txt')
ev = json.load(open('logs/tas4751.events.json'))['stages']
for s in ev[12:]:
    a = s['control']; b = s.get('boss0') or (s['control']+s.get('control_to_next_load',300))
    if s['name']=='6-5': b = 39084
    sl = rows[a-1:b]   # frames a..b
    rep = check(sl, windows=((600,109),(1800,246)))
    v = {k:(r['violations'], r.get('by_button')) for k,r in rep['rules'].items() if r['violations']}
    pr = {k:(st['presses'], st['max_presses_in_60_frames']) for k,st in rep['stats'].items() if st['presses']}
    print(s['name'], a, b, b-a, v); print('    presses', pr)
