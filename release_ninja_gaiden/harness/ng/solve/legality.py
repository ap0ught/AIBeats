"""ng.solve.legality - ONE place for the project's human input rules (knowledge/project_rules.md, APPROVED cap).

    RULES                         period 5, hold 2, release 2, windows 600:109 / 1800:246, no L+R, no U+D
    Enforcer(history)             online: .emit(wanted_row) -> nearest legal row (committed). Re-export of
                                  a56_common.Enforcer (used by StageBeam, jplan, jq3, a12r2_solve).
    legalize(rows, history)       open loop: every row through a fresh Enforcer (greedy, retries blocked presses)
    project(rows, history)        open loop with look-ahead: ng.legal.project (resolve L+R/U+D + DP press repair)
    Legality(history)             ng.legal.Legality: .can(row) / .why(row) / .fix(row) / .push(row)
    check(rows, history) -> dict  the judge = check_inputs.check() on history + rows ("pass", "violations", ...)
    check_file(path, history_path=None) -> dict
    assert_legal(rows, history)   raises ValueError with the first reasons

check_inputs.py is the judge; the Enforcer / Legality are only generators. Every published file is re-judged by
check() (or `python check_inputs.py <file> --period 5 --hold 2 --release 2 --windows 600:109,1800:246`) on the FULL
power-on input list (the 600/1800 windows cross stage boundaries).
"""
from __future__ import annotations

from . import common as _c  # noqa: F401  (sets sys.path)

import a56_common as _a56  # noqa: E402
from ng import legal as _legal  # noqa: E402

RULES = dict(_legal.RULES)
Enforcer = _a56.Enforcer
Legality = _legal.Legality
project = _legal.project
enforce = _legal.enforce
resolve_opposing = _legal.resolve_opposing


def legalize(rows, history=(), retry=3):
    return _a56.legalize(rows, history, retry)


def check(rows, history=()) -> dict:
    return _legal.check(list(rows), list(history))


def check_file(path, history_path=None) -> dict:
    rows = _c.rows_of(path)
    hist = _c.rows_of(history_path) if history_path else []
    return check(rows, hist)


def assert_legal(rows, history=()):
    r = check(rows, history)
    if not r.get("pass"):
        raise ValueError(f"illegal input: {str(r)[:400]}")
    return r


def cmdline(path) -> str:
    """The exact judge command for a power-on input file."""
    return f'python check_inputs.py "{path}" --period 5 --hold 2 --release 2 --windows 600:109,1800:246'
