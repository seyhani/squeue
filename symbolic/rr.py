from typing import List, Dict

from z3 import If, Implies, And, Not, ModelRef, ExprRef, IntVal, ArithRef, BoolRef, ArrayRef, BoolVal

from symbolic.arr import IntArray
from symbolic.base import SymbolicStructure
from symbolic.queue import SymbolicQueue
from symbolic.util import find_idx_expr, memoize


class RoundRobinScheduler(SymbolicStructure):
    in_queue_size: int
    queues: List[SymbolicQueue]
    out: IntArray

    def __init__(self, name: str, in_queue_size: int, hists: List[IntArray]):
        super().__init__(name)
        self.in_queue_size = in_queue_size
        self.total_time = hists[0].size
        self.queues = [SymbolicQueue("q_{}".format(i), in_queue_size, h) for i, h in enumerate(hists)]
        self.out = IntArray("qo", self.total_time)

    def constrs(self) -> List[ExprRef]:
        constrs = []
        for queue in self.queues:
            constrs.extend(queue.constrs())
        constrs.extend(self.out.constrs())
        return constrs

    def no_deq(self, t) -> BoolRef:
        return And([q.deqs[t] == 0 for q in self.queues])

    def deqs(self, t) -> List[ArrayRef]:
        return [q.deqs[t] for q in self.queues]

    def next_candidate_serve(self, t) -> ArithRef:
        return (self.last_served(t - 1) + IntVal(1)) % len(self.queues)

    @memoize
    def last_served(self, t) -> ArithRef:
        if t == 0:
            return IntVal(len(self.queues) - 1)
        return If(self.no_deq(t), self.last_served(t - 1),
                  find_idx_expr(self.deqs(t), IntVal(1))
                  )

    def eval(self, model: ModelRef):
        pass

    def ls_constrs(self, t):
        constrs = []
        q1_empty = self.queues[0].blog(t) == 0
        q2_empty = self.queues[1].blog(t) == 0
        ci = (self.last_served[t - 1] % 2) + 1
        constrs.append(Implies(And(q1_empty, q2_empty), self.last_served[t] == self.last_served[t - 1]))
        constrs.append(Implies(And(Not(q1_empty), q2_empty), self.last_served[t] == 1))
        constrs.append(Implies(And(q1_empty, Not(q2_empty)), self.last_served[t] == 2))
        constrs.append(
            Implies(And(Not(q1_empty), Not(q2_empty)), If(ci == 1, self.last_served[t] == 1, self.last_served[t] == 2)))
        return constrs

    def not_empty(self, t) -> IntArray:
        pass

    def out_constrs(self, t):

        constrs = []
        for i in range(len(self.queues)):
            constr = And()
            candidate = self.next_candidate_serve(t)
            previous_queues_empty_expr = BoolVal(True)
            for j in range(i):
                pass
            constr = And(self.not_empty(t)[candidate] == 1, )


        q1_empty = self.queues[0].blog(t) == 0
        q2_empty = self.queues[1].blog(t) == 0
        ci = (self.last_served[t - 1] % 2) + 1
        constrs.append(Implies(And(q1_empty, q2_empty), self.out[t + 1] == 0))
        constrs.append(Implies(And(Not(q1_empty), q2_empty), self.out[t + 1] == self.queues[0].head_pkt(t)))
        constrs.append(Implies(And(q1_empty, Not(q2_empty)), self.out[t + 1] == self.queues[1].head_pkt(t)))
        constrs.append(
            Implies(And(Not(q1_empty), Not(q2_empty)), If(ci == 1,
                                                          self.out[t + 1] == self.queues[0].head_pkt(t),
                                                          self.out[t + 1] == self.queues[1].head_pkt(t))))
        return constrs

    def deq_constrs(self, t):
        constrs = []
        q1_empty = self.queues[0].blog(t) == 0
        q2_empty = self.queues[1].blog(t) == 0
        ci = (self.last_served[t - 1] % 2) + 1
        constrs.append(Implies(And(q1_empty, q2_empty), And(self.queues[0].deqs[t] == 0, self.queues[1].deqs[t] == 0)))
        constrs.append(
            Implies(And(Not(q1_empty), q2_empty), And(self.queues[0].deqs[t] == 1, self.queues[1].deqs[t] == 0)))
        constrs.append(
            Implies(And(q1_empty, Not(q2_empty)), And(self.queues[0].deqs[t] == 0, self.queues[1].deqs[t] == 1)))
        constrs.append(
            Implies(And(Not(q1_empty), Not(q2_empty)), If(ci == 1,
                                                          And(self.queues[0].deqs[t] == 1, self.queues[1].deqs[t] == 0),
                                                          And(self.queues[0].deqs[t] == 0,
                                                              self.queues[1].deqs[t] == 1))))
        return constrs

    def run(self):
        constrs = [self.last_served[0] == 2]
        constrs.append(self.out[1] == 0)
        for t in range(1, TOTAL_TIME):
            constrs.extend(self.ls_constrs(t))
            constrs.extend(self.deq_constrs(t))
            constrs.extend(self.out_constrs(t))
        self.constrs.extend(constrs)
