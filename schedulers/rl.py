from typing import List

from z3 import ExprRef, Implies, ModelRef, If, And

from symbolic.base import TimeIndexedStructure
from symbolic.hist import SymbolicHistory
from symbolic.squeue import SymbolicQueue


class RateLimiter(TimeIndexedStructure):
    in_queue_size: int
    queue: SymbolicQueue
    out: SymbolicHistory
    __constrs: List[ExprRef]

    def __init__(self, name: str, total_time: int, in_queue_size: int, hist: SymbolicHistory):
        super().__init__(name=name, total_time=total_time)
        self.__constrs = []
        self.in_queue_size = in_queue_size
        self.queue = SymbolicQueue("{}_q".format(name), in_queue_size, hist)
        self.out = SymbolicHistory(name="{}_qo".format(name), total_time=self.total_time)

    def constrs(self) -> List[ExprRef]:
        constrs = []
        constrs.extend(self.out.constrs())
        constrs.extend(self.queue.constrs())
        constrs.extend(self.__constrs)
        return constrs

    def run(self):
        constrs = []
        q = self.queue
        constrs.append(q.deqs[0] == 0)
        for t in range(1, self.total_time):
            constrs.append(If(And(q.deqs[t - 1] == 0, q.blog(t) > 0), q.deqs[t] == 1, q.deqs[t] == 0))
            self.__constrs.append(If(self.queue.deqs[t] == 1, self.out[t] == self.queue.head_pkt(t), self.out[t] == 0))
            pass
        self.__constrs.extend(constrs)

    def eval(self, model: ModelRef):
        return self.out.eval(model)
