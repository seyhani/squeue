from typing import Dict, List

from z3 import Solver, ExprRef, sat, unsat, ModelRef

from symbolic.base import SymbolicStructure, LabeledExpr
from utils.logger import Logger

RANDOM_SEED = 100


class SmtSolver:
    solver: Solver
    structs: Dict[str, SymbolicStructure]
    constrs: Dict[str, ExprRef]

    def __init__(self, seed=RANDOM_SEED):
        solver = Solver()
        solver.set('smt.arith.random_initial_value', True)
        solver.set('random_seed', seed)
        solver.set(unsat_core=True)
        self.solver = solver
        self.structs = {}
        self.constrs = {}

    def add_struct(self, struct: SymbolicStructure):
        self.add_constrs(struct.constrs())
        self.structs[struct.name] = struct

    def add_constr(self, expr: ExprRef, label: str = None):
        if label is None:
            label = str(expr)
            Logger.warn("Using implicit label for constr: {}".format(str(expr)))

        if label in self.constrs:
            Logger.warn("Duplicate constraint label: {}".format(label))

        self.constrs[label] = expr
        self.solver.assert_and_track(expr, label)

    def add_constrs(self, constrs: List[LabeledExpr]):
        for constr in constrs:
            if not isinstance(constr, LabeledExpr):
                raise RuntimeError("Constraint must be labeled: " + str(constr))
            self.add_constr(constr.expr, constr.label)

    def for_all(self, constr_producer, time_range):
        for t in range(time_range[0], time_range[1]):
            constr = constr_producer(t)
            self.add_constr(constr)

    def check_sat(self) -> ModelRef:
        res = self.solver.check()
        if res != sat:
            raise RuntimeError("Model is not SAT")
        return self.solver.model()

    def check_unsat(self) -> List[ExprRef]:
        res = self.solver.check()
        if res != unsat:
            raise RuntimeError("Model is SAT")
        return self.solver.unsat_core()
