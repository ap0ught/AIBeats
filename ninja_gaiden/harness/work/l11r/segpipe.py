"""Run work/l11r/segga.py over consecutive segments of a stage (each from the previous segment's Mesen end state).
    python -u work/c5/segpipe.py <spec.json>
spec: {"tag": "p22", "hist": <power-on rows up to the start>, "mst": <Mesen state at the start>,
       "prefix": <rows already fixed in this stage (written first into the output)> | null,
       "seed": <seed rows file (positions: index 0 = the stage-relative row `seed_t0`)>, "seed_t0": 207,
       "segs": [{"goal": "x:6:le:384", "from": 207, "to": 437, "mins": 20, "opts": ["--npb", "12"]}, ...],
       "workers": 2}
'from' / 'to' = the seed's stage-relative rows where the previous / this goal was reached (seed slice = from..to).
Writes states/tmp/c5_<tag>_stage.inputs.txt (prefix + all segment rows) and logs/c5/<tag>.pipe.json."""
import json
import os
import subprocess
import sys

sys.path.insert(0, '.')
from ng.solve import common as C  # noqa: E402

spec = json.load(open(sys.argv[1]))
tag = spec['tag']
hist = C.rows_of(spec['hist'])
pre = C.rows_of(spec['prefix']) if spec.get('prefix') else []
seed = C.rows_of(spec['seed'])
t0 = spec['seed_t0']
mst = spec['mst']
stage_rows = list(pre)
log = []
for k, sg in enumerate(spec['segs']):
    st = f"{tag}_s{k}"
    hf = f"states/tmp/l11_{st}_hist.inputs.txt"
    C.write_inputs(hf, hist + stage_rows, f"history for {st}")
    sf = f"states/tmp/l11_{st}_seed.inputs.txt"
    a, b = sg['from'] - t0, sg['to'] - t0 + 12
    C.write_inputs(sf, seed[a:b], f"seed {st}")
    cmd = [sys.executable, '-u', 'work/l11r/segga.py', hf, mst, sf, sg['goal'], st, '--mins', str(sg.get('mins', 20)),
           '--workers', str(spec.get('workers', 2)), '--extra', str(sg.get('extra', 30))] + sg.get('opts', [])
    print('RUN', ' '.join(cmd), flush=True)
    with open(f"work/l11r/{st}.out", 'w') as fo:
        r = subprocess.run(cmd, stdout=fo, stderr=subprocess.STDOUT)
    info_f = f"states/tmp/l11_{st}.json"
    if r.returncode != 0 or not os.path.exists(info_f):
        print('FAILED', st, r.returncode, flush=True)
        break
    info = json.load(open(info_f))
    rows = C.rows_of(f"states/tmp/l11_{st}.inputs.txt")
    stage_rows += rows
    mst = f"states/mesen/l11_{st}g.mst"
    info['stage_t'] = len(stage_rows)
    info['orig_t'] = sg['to']
    log.append(info)
    print('SEG', json.dumps(info), flush=True)
    C.write_inputs(f"states/tmp/l11_{tag}_stage.inputs.txt", stage_rows, f"segpipe {tag} through {st} (Mesen; verify)")
    json.dump(log, open(f"work/l11r/{tag}.pipe.json", 'w'), indent=1)
print('DONE', len(stage_rows), flush=True)
