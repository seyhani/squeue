from typing import List

from z3 import If, Implies, And, ModelRef, IntVal, ArithRef

from symbolic.arr import IntArray
from symbolic.base import TimeIndexedStructure, LabeledExpr
from symbolic.hist import SymbolicHistory
from symbolic.squeue import SymbolicQueue
from symbolic.util import ZERO


class RoundRobinScheduler(TimeIndexedStructure):
    in_queue_size: int
    queues: List[SymbolicQueue]
    out: SymbolicHistory
    empty: List[IntArray]
    served: IntArray

    def __init__(self, name: str, total_time: int, in_queue_size: int, hists: List[SymbolicHistory]):
        super().__init__(name=name, total_time=total_time)
        self.in_queue_size = in_queue_size
        self.queues = [SymbolicQueue("{}::q_{}".format(name, i), in_queue_size, h) for i, h in enumerate(hists)]
        self.out = SymbolicHistory(name="{}::out".format(name), total_time=self.total_time)
        self.served = IntArray(name="{}::served".format(name), size=self.total_time)
        self.empty = []
        self.setup_empties()
        self.add_served_constrs()

    def setup_empties(self):
        for t in range(self.total_time):
            empty = IntArray(name="{}::empty_{}".format(self.name, t), size=len(self.queues))
            for i in range(len(self.queues)):
                empty.add_constr(LabeledExpr(
                    empty[i] == If(self.queues[i].blog(t) == 0, 1, 0),
                    "{0}::empty_{1}[{2}] = {3} <=> q_{1}::blog({2}) = {4}".format(self.name, i, t, 1, 0)
                ))
            self.empty.append(empty)

    def add_served_constrs(self):
        self.served.add_constr(LabeledExpr(
            self.served[0] == IntVal(len(self.queues) - 1),
            "{0}::served[{1}] = {2}".format(self.name, 0, len(self.queues) - 1)
        ))
        for t in range(self.total_time):
            self.served.add_constr(
                LabeledExpr(
                    self.served[t] >= -1,
                    "{0}::served[{1}] >= {2}".format(self.name, t, -1)
                )
            )
            self.served.add_constr(
                LabeledExpr(
                    self.served[t] <= len(self.queues),
                    "{0}::served[{1}] <= {2}".format(self.name, t, len(self.queues))
                )
            )

    def constrs(self) -> List[LabeledExpr]:
        constrs = []
        constrs.extend(self.out.constrs())
        constrs.extend(self.served.constrs())
        for queue in self.queues:
            constrs.extend(queue.constrs())
        for e in self.empty:
            constrs.extend(e.constrs())
        constrs.extend(self.scheduling_constrs())
        return constrs

    def candidate(self, t) -> ArithRef:
        return (self.last_served(t) + 1) % len(self.queues)

    def last_served(self, t) -> ArithRef:
        if t == 0:
            return self.served[0]
        return If(self.served[t] >= 0, self.served[t], self.last_served(t - 1))

    def all_empty(self, t) -> ArithRef:
        return And([self.empty[t][i] == 1 for i in range(self.empty[t].size)])

    def queue_select_constrs(self, t) -> List[LabeledExpr]:
        constrs = [LabeledExpr(
            Implies(self.all_empty(t), self.served[t] == -1),
            "{0}:: all_empty({1}) => served[{1}] = {2}".format(self.name, t, -1)
        )]
        for i in range(len(self.queues)):
            cidx = self.candidate(t - 1)
            ands = []
            for j in range(i):
                idx = (cidx + j) % len(self.queues)
                ands.append(self.empty[t][idx] == True)
            idx = (cidx + i) % len(self.queues)
            constr = And(*ands, self.empty[t][idx] == False)
            constrs.append(
                LabeledExpr(
                    Implies(constr, self.served[t] == idx),
                    # TODO: Label is not correct
                    "{0}:: prevs_empty({1}) & not_empty({1}) => served[{2}] == {1}".format(self.name, i, t)
                )
            )
        return constrs

    def push_out_constrs(self, t) -> List[LabeledExpr]:
        constrs = [LabeledExpr(
            Implies(self.served[t] == IntVal(-1), self.out[t] == ZERO),
            "{0}:: served[{1}] = {2} => out[{1}] = {3}".format(self.name, t, -1, 0)
        )]
        for i in range(len(self.queues)):
            constrs.append(
                LabeledExpr(
                    Implies(self.served[t] == IntVal(i), self.out[t] == self.queues[i].head_pkt(t)),
                    "{0}:: served[{1}] = {2} => out[{1}] = q_{2}::head_pkt({1})".format(self.name, t, i)
                )
            )
        return constrs

    def dequeue_constrs(self, t) -> List[LabeledExpr]:
        constrs = []
        for i, q in enumerate(self.queues):
            constrs.append(
                LabeledExpr(
                    If(self.served[t] == IntVal(i), q.deqs[t] == 1, q.deqs[t] == 0),
                    "{0}:: q_{1}::deqs[{2}] == {3} <=> served[{2}] == {1}".format(self.name, t, i, 1)
                )
            )
        return constrs

    def scheduling_constrs(self):
        constrs = []
        for t in range(1, self.total_time):
            constrs.extend(self.queue_select_constrs(t))
            constrs.extend(self.push_out_constrs(t))
            constrs.extend(self.dequeue_constrs(t))
        return constrs

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
