from typing import List

from z3 import Solver, sat, unsat

from symbolic.base import SymbolicStructure, LabeledExpr
from symbolic.smt_solver import SmtSolver


def instantiate(struct: SymbolicStructure, constrs: List[LabeledExpr] = []):
    s = SmtSolver()
    s.add_struct(struct)
    s.add_constrs(constrs)
    m = s.check_sat()
    return struct.eval(m)


def assert_unsat(struct: SymbolicStructure):
    s = SmtSolver()
    s.add_struct(struct)
    return s.check_unsat()

