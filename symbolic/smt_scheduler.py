from typing import List

from z3 import If, Implies, And, Not

from mem_smt_queue import MemSymbolicQueue
from symbolic.queue import SymbolicQueue, IntArray, TOTAL_TIME


class SmtRoundRobinScheduler:
    queues: List[SymbolicQueue]
    out: IntArray
    last_served: IntArray

    def __init__(self, h1, h2):
        self.queues = []
        self.queues.append(MemSymbolicQueue("q1", h1))
        self.queues.append(MemSymbolicQueue("q2", h2))
        self.out = IntArray("qo", [0])
        self.last_served = IntArray("ls", [2])
        self.constrs = []
        self.constrs.extend(self.queues[0].constrs)
        self.constrs.extend(self.queues[1].constrs)
        self.constrs.extend(self.out.constrs)
        self.constrs.extend(self.last_served.constrs)

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

    def out_constrs(self, t):
        constrs = []
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
