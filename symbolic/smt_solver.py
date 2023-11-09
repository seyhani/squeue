from typing import Callable, Dict, List

from z3 import Solver, Z3Exception, ExprRef, sat, unsat, ArrayRef, Model, ModelRef

from symbolic.base import SymbolicStructure, Time, TimeRange, LabeledConstraint

RANDOM_SEED = 100

TimedExprProducer = Callable[[Time], ExprRef]


class SmtSolver:
    solver: Solver
    structs: Dict[str, SymbolicStructure]

    def __init__(self):
        solver = Solver()
        solver.set('smt.arith.random_initial_value', True)
        solver.set('random_seed', RANDOM_SEED)
        solver.set(unsat_core=True)
        self.solver = solver
        self.structs = {}

    def add_struct(self, struct: SymbolicStructure):
        print("\n\tAdding constraints for: {} \n".format(struct.name))
        for c in struct.constrs():
            self.add_constr(c)
        self.structs[struct.name] = struct

    def add_constr(self, constr: ExprRef):
        self.solver.add(constr)
        # try:
        #     self.solver.assert_and_track(constr.expr, constr.label)
        # except Z3Exception as e:
        #     print("Failed to add constraint: {}".format(constr.label))
        #     print(e)

    def for_all(self, constr_producer: TimedExprProducer, time_range: TimeRange):
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
