from typing import List

from symbolic.base import SymbolicStructure, LabeledExpr
from symbolic.smt_solver import SmtSolver


def instantiate(struct: SymbolicStructure, constrs: List[LabeledExpr] = None):
    if constrs is None:
        constrs = []
    s = SmtSolver()
    s.add_struct(struct)
    s.add_constrs(constrs)
    m = s.check_sat()
    return struct.eval(m)


def assert_unsat(struct: SymbolicStructure):
    s = SmtSolver()
    s.add_struct(struct)
    return s.check_unsat()
