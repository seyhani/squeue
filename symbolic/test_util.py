from z3 import Solver, sat, unsat

from symbolic.base import SymbolicStructure


def instantiate(struct: SymbolicStructure):
    s = Solver()
    s.add(struct.constrs())
    assert s.check() == sat, "{} is not SAT!".format(struct.name)
    m = s.model()
    return struct.eval(m), struct.eval_to_str(m)


def assert_unsat(struct: SymbolicStructure):
    s = Solver()
    s.add(struct.constrs())
    assert s.check() == unsat
