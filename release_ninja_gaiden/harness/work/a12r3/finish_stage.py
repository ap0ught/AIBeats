"""Finish a stage from our rows: play rows, then blank rows (Start skip on the cutscene) to the next stage's control,
verify open-loop from the start state, legality with history, save the end state and the stage files.

    python work/a12r3/finish_stage.py <stage 0..4> <start state> <history> <rows> N <out name>
-> logs/<out>.inputs.txt, logs/<out>.json, states/<out>_end.State
"""
import json
import sys
sys.path.insert(0, 'ng/stages')
sys.path.insert(0, '.')
import a56_common as C  # noqa: E402
import a12r2_solve as S  # noqa: E402
from ng.inputs import read_inputs, write_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402

stage, start, hf, f, N, out = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6]
history = [tuple(r) for r in read_inputs(hf)]
rows = [tuple(r) for r in read_inputs(f)][:N]
e = C.open_emu('a12r3_probe.log')
try:
    e.tick(TICKS)
    st = e.load(start)
    f0 = st['frame']
    e.run(rows)
    tail = S.to_control(e, stage, history + rows)
    rows = rows + tail
    rep = S.verify(e, stage, start, rows, history)
    e.save(f'{out}_end')
    rep.update({'stage': S.NAMES[stage], 'start': start, 'end_state': f'{out}_end',
                'tas_frames': S.TAS_FRAMES.get(stage), 'record_frames': S.RECORD_FRAMES.get(stage)})
    rep['vs_tas'] = rep['frames'] - S.TAS_FRAMES.get(stage, 0)
    rep['vs_record'] = round(rep['frames'] - S.RECORD_FRAMES.get(stage, 0), 1)
    write_inputs(f'logs/{out}.inputs.txt', rows, f'a12r3 stage {S.NAMES[stage]} from {start} (frame {f0}) to the next '
                                                 f'control {rep["control_frame"]}; legal={rep["legal"]}')
    with open(f'logs/{out}.json', 'w', encoding='utf-8') as fh:
        json.dump(rep, fh, indent=1)
    print('RESULT', json.dumps(rep), flush=True)
finally:
    e.close()
