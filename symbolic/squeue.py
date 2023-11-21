from typing import List, Dict

from z3 import If, IntVal, Or, ModelRef, ArithRef, And

from symbolic.arr import IntArray
from symbolic.base import TimeIndexedStructure, LabeledExpr
from symbolic.hist import SymbolicHistory
from symbolic.util import min_expr, memoize, ZERO


class SymbolicQueue(TimeIndexedStructure):
    hist: SymbolicHistory
    deqs: IntArray

    def __init__(self, name: str, size: int, hist: SymbolicHistory):
        super().__init__(name=name, total_time=hist.size)
        self.size = size
        self.hist = hist
        self.deqs = IntArray(name="{}::deqs".format(name), size=self.total_time)
        self.deqs.add_constr(LabeledExpr(self.deqs[0] == 0, "{}::deqs[{}] == {}".format(self.name, 0, 0)))
        for t in range(self.total_time):
            self.deqs.add_constr(LabeledExpr(self.deqs[t] >= 0, "{}::deqs[{}] >= {}".format(self.name, t, 0)))
            self.deqs.add_constr(
                LabeledExpr(self.deqs[t] <= self.blog(t), "{0}::deqs[{1}] <= blog({1})".format(self.name, t)))

    def constrs(self) -> List[LabeledExpr]:
        constrs = []
        constrs.extend(self.hist.constrs())
        constrs.extend(self.deqs.constrs())
        return constrs

    def set_dequeues(self, deqs_dict: Dict[int, int]):
        for t in range(self.total_time):
            val = 0
            if t in deqs_dict:
                val = deqs_dict[t]
            self.deqs.add_constr(LabeledExpr(self.deqs[t] == val, "{}::deqs[{}] = {}".format(self.name, t, val)))

    def eval(self, model: ModelRef):
        concrete_queue = [[]]
        for t in range(1, self.total_time):
            elems = []
            for i in range(model.eval(self.blog(t)).as_long()):
                elem_idx = model.eval(self.tail(t, i))
                elems.insert(0, model.eval(self.hist[elem_idx]))
            concrete_queue.append(elems)
        return concrete_queue

    def arr(self, t) -> ArithRef:
        return If(self.hist[t] > ZERO, 1, 0)

    @memoize
    def cdeq(self, t) -> ArithRef:
        if t == 0:
            return self.deqs[0]
        return self.cdeq(t - 1) + self.deqs[t]

    @memoize
    def cap(self, t) -> ArithRef:
        return self.size - (self.blog(t) - self.deqs[t])

    @memoize
    def enq(self, t) -> ArithRef:
        return min_expr(self.arr(t), self.cap(t))

    @memoize
    def cenq(self, t) -> ArithRef:
        if t == 0:
            return ZERO
        return self.cenq(t - 1) + self.enq(t)

    @memoize
    def blog(self, t) -> ArithRef:
        if t == 0:
            return ZERO
        return self.blog(t - 1) - self.deqs[t - 1] + self.enq(t - 1)

    @memoize
    def tail(self, t, i) -> ArithRef:
        if t == 0:
            return ZERO
        return If(Or(i > self.blog(t), self.blog(t) == ZERO),
                  ZERO,
                  If(self.enq(t - 1) == 1,
                     If(i == 0,
                        IntVal(t - 1),
                        self.tail(t - 1, i - 1)
                        ),
                     self.tail(t - 1, i))
                  )

    @memoize
    def head(self, t) -> ArithRef:
        return self.tail(t, self.blog(t) - 1)

    @memoize
    def drop(self, t) -> ArithRef:
        return If(And(self.arr(t) == 1, self.enq(t) == 0), 1, 0)

    @memoize
    def head_pkt(self, t) -> ArithRef:
        return self.hist[self.head(t)]

    def eval_to_str(self, model: ModelRef):
        return """
        \r      \t {}
        \r hist:\t {}
        \r drop:\t {}
        \r  arr:\t {}
        \r  cap:\t {}
        \r  deq:\t {}
        \r  enq:\t {}
        \r cenq:\t {}
        \r cdeq:\t {}
        \r blog:\t {}
        \r head:\t {}
        """.format(
            [t for t in range(self.total_time)],
            self.hist.eval(model),
            self.eval_timed_metric(self.drop, model),
            self.eval_timed_metric(self.arr, model),
            self.eval_timed_metric(self.cap, model),
            self.deqs.eval(model),
            self.eval_timed_metric(self.enq, model),
            self.eval_timed_metric(self.cenq, model),
            self.eval_timed_metric(self.cdeq, model),
            self.eval_timed_metric(self.blog, model),
            self.eval_timed_metric(self.head, model)
        )
