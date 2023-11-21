from typing import List

from z3 import ModelRef, If, And

from symbolic.base import TimeIndexedStructure, LabeledExpr
from symbolic.hist import SymbolicHistory
from symbolic.squeue import SymbolicQueue
from symbolic.util import memoize


class RateLimiter(TimeIndexedStructure):
    in_queue_size: int
    queue: SymbolicQueue
    out: SymbolicHistory

    def __init__(self, name: str, total_time: int, in_queue_size: int, hist: SymbolicHistory):
        super().__init__(name=name, total_time=total_time)
        self.in_queue_size = in_queue_size
        self.queue = SymbolicQueue("{}::q".format(name), in_queue_size, hist)
        self.out = SymbolicHistory(name="{}::out".format(name), total_time=self.total_time)

    def constrs(self) -> List[LabeledExpr]:
        constrs = []
        constrs.extend(self.out.constrs())
        constrs.extend(self.queue.constrs())
        constrs.extend(self.scheduling_constrs())
        return constrs

    @memoize
    def scheduling_constrs(self) -> List[LabeledExpr]:
        constrs = []
        q = self.queue
        constrs.append(LabeledExpr(q.deqs[0] == 0, "{}::deqs[{}] = {} ".format(self.name, 0, 0)))
        for t in range(1, self.total_time):
            constrs.append(
                LabeledExpr(
                    If(And(q.deqs[t - 1] == 0, q.blog(t) > 0), q.deqs[t] == 1, q.deqs[t] == 0),
                    "{0}::deqs[{1}] = 1 <=> deqs[{1}-1] == 0".format(self.name, t)
                )
            )
            constrs.append(
                LabeledExpr(
                    If(self.queue.deqs[t] == 1, self.out[t] == self.queue.head_pkt(t), self.out[t] == 0),
                    "{0}::out[{1}] = q.head({1}) <=> deqs[{1}] == 1".format(self.name, t)
                )
            )
        return constrs

    def eval(self, model: ModelRef):
        return self.out.eval(model)
