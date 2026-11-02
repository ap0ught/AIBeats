"""ng.solve - the shared Ninja Gaiden legal-run toolkit (one package over the act agents' solvers).

Documentation: knowledge/toolkit.md. Modules (each has its own doc and most a `python -m ng.solve.<m>` CLI):

  common     paths, stage names / rooms, TAS + record splits (record_events.json), rows I/O, open_emu
  legality   the rules in one place: Enforcer (online), legalize / project (open loop), Legality, check (judge)
  hitbox     Ryu / sword / enemy / lantern / thrown boxes from RAM (community Lua scripts, checked against bank07)
  items      every lantern from the ROM tables + the owner's maps index; ninpo / weapon planner over a route
  beam       stage beam (a56_beam.StageBeam) with reference modes tas / record / hybrid, any stage, boss mode
  astar      macro A* over stable states (a34r2_astar, unchanged) for any stage
  boss       whole-jump boss planner (work/a56r2/jplan.py, unchanged) for any boss state
  verify     finish a stage to the next control + open-loop verify + judge + record; power-on chain assembly
  fast       Mesen search backend (ng/fastcore.py): boot from a power-on history, batch candidates, `slash` CLI
  compare    per-room/column first-reach times vs the TAS, hp/ninpo/item changes
  record     record splits and traced record routes
  jobq       RAM-gated job queue (free RAM >= 2.5 GB, <= 3 jobs, 1 while a HOLD_FARMS exists), PID tracking
  results    logs/results.json - the standard per-stage result record

Nothing here edits the act agents' files: their modules are imported read-only (ng/legal.py, ng/stages/a56_*.py,
a34_core.py, a34r2_astar.py, a12r2_solve.py, work/a56r2/jplan.py) and wrapped.
"""
