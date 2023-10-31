from typing import List, Dict

from z3 import If, Implies, And, Not, ModelRef, ExprRef, IntVal, ArithRef, BoolRef, ArrayRef, BoolVal, Store, Select

from symbolic.arr import IntArray, BoolArray
from symbolic.base import SymbolicStructure
from symbolic.queue import SymbolicQueue
from symbolic.util import find_idx_expr, memoize, eq, gte, lte, ZERO


class RoundRobinScheduler(SymbolicStructure):
    in_queue_size: int
    queues: List[SymbolicQueue]
    out: IntArray
    empty: List[BoolArray]
    served: IntArray
    __constrs: List[ExprRef]

    def __init__(self, name: str, in_queue_size: int, hists: List[IntArray]):
        super().__init__(name)
        self.__constrs = []
        self.in_queue_size = in_queue_size
        self.total_time = hists[0].size
        self.queues = [SymbolicQueue("q_{}".format(i), in_queue_size, h) for i, h in enumerate(hists)]
        self.out = IntArray("qo", self.total_time)
        self.served = IntArray("served", self.total_time)
        self.empty = []
        for t in range(self.total_time):
            empty = BoolArray("empty[{}]".format(t), len(self.queues))
            for i in range(len(self.queues)):
                empty.add_constr(i, eq((self.queues[i].blog(t) == 0)))
            self.empty.append(empty)

    def constrs(self) -> List[ExprRef]:
        constrs = []
        constrs.extend(self.out.constrs())
        constrs.extend(self.served.constrs())
        for queue in self.queues:
            constrs.extend(queue.constrs())
        for e in self.empty:
            constrs.extend(e.constrs())
        constrs.extend(self.__constrs)
        return constrs

    def candidate(self, t) -> ArithRef:
        return (self.last_served(t) + 1) % len(self.queues)

    def last_served(self, t) -> ArithRef:
        if t == 0:
            return self.served[0]
        return If(self.served[t] >= 0, self.served[t], self.last_served(t - 1))

    def all_empty(self, t) -> BoolRef:
        return And([self.empty[t][i] for i in range(self.empty[t].size)])

    def pick_queue(self, t):
        constrs = [Implies(self.all_empty(t), self.served[t] == -1)]
        for i in range(len(self.queues)):
            cidx = self.candidate(t - 1)
            ands = []
            for j in range(i):
                idx = (cidx + j) % len(self.queues)
                ands.append(self.empty[t][idx] == True)
            idx = (cidx + i) % len(self.queues)
            constr = And(*ands, self.empty[t][idx] == False)
            constrs.append(Implies(constr, self.served[t] == idx))
        self.__constrs.extend(constrs)

    def push_out(self, t):
        constrs = []
        constrs.append(Implies(self.served[t] == IntVal(-1), self.out[t] == ZERO))
        for i in range(len(self.queues)):
            constrs.append(Implies(self.served[t] == IntVal(i), self.out[t] == self.queues[i].head_pkt(t)))
        self.__constrs.extend(constrs)

    def dequeue(self, t):
        constrs = []
        for i, q in enumerate(self.queues):
            constrs.append(If(self.served[t] == IntVal(i), q.deqs[t] == 1, q.deqs[t] == 0))
        self.__constrs.extend(constrs)

    def run(self):
        self.served.add_constr(0, eq(IntVal(len(self.queues) - 1)))
        for t in range(self.total_time):
            self.served.add_constr(t, gte(IntVal(-1)))
            self.served.add_constr(t, lte(IntVal(len(self.queues))))
        for t in range(1, self.total_time):
            self.pick_queue(t)
            self.push_out(t)
            self.dequeue(t)

    def eval(self, model: ModelRef):
        return self.out.eval(model)

    def eval_queues_to_str_step(self, model: ModelRef, t):
        res = "\r"
        for i, q in enumerate(self.queues):
            res += "q[{}]:\t {}\n".format(i, q.eval(model)[t])
        return res

    def eval_to_str_step(self, model: ModelRef, t):
        return """
        \r----RR@[{}]----
        \rempty:\t {} 
        {}
        \r---------------
        """.format(t,
                   self.empty[t].eval(model),
                   self.eval_queues_to_str_step(model, t)
                   )

    def eval_to_str(self, model: ModelRef) -> str:
        return """
        \r {}
        \r all_empty:\t {}
        \r    served:\t {}
        \r  last_srv:\t {}
        \r candidate:\t {}
        \r       out:\t {}
        """.format(
            "".join([self.eval_to_str_step(model, t) for t in range(self.total_time)]),
            [model.eval(self.all_empty(t)) for t in range(self.total_time)],
            self.served.eval(model),
            [model.eval(self.last_served(t)) for t in range(self.total_time)],
            [model.eval(self.candidate(t)) for t in range(self.total_time)],
            self.out.eval(model)
        )
