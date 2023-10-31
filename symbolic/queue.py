from typing import List

from z3 import If, IntVal, Or, ModelRef, ExprRef, ArithRef, ArrayRef

from symbolic.arr import IntArray
from symbolic.base import SymbolicStructure, TimeIndexedStructure
from symbolic.util import min_expr, memoize, eq, gte, ZERO, lte


class SymbolicQueue(TimeIndexedStructure):
    hist: IntArray
    deqs: IntArray

    def __init__(self, name: str, size: int, hist: IntArray):
        super().__init__(name, hist.size)
        self.size = size
        self.hist = hist
        self.deq_constrs = {}
        self.deqs = IntArray("{}_deqs".format(name), self.total_time)
        self.deqs.add_constr(0, eq(ZERO))
        for t in range(self.total_time):
            self.deqs.add_constr(t, gte(ZERO))
        for t in range(self.total_time):
            self.deqs.add_constr(t, lte(self.blog(t)))

    def constrs(self) -> List[ExprRef]:
        constrs = []
        constrs.extend(self.deq_constrs.values())
        constrs.extend(self.hist.constrs())
        constrs.extend(self.deqs.constrs())
        return constrs

    def eval(self, model: ModelRef):
        concrete_queue = [[]]
        for t in range(1, self.total_time):
            elems = []
            for i in range(model.eval(self.blog(t)).as_long()):
                elem_idx = model.eval(self.tail(t, i))
                elems.insert(0, model.eval(self.hist[elem_idx]))
            concrete_queue.append(elems)
        return concrete_queue

    def arr(self, t) -> ExprRef:
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
    def enq(self, t) -> ExprRef:
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

    def head(self, t) -> ArithRef:
        return self.tail(t, self.blog(t) - 1)

    def head_pkt(self, t) -> ArrayRef:
        return self.hist[self.head(t)]

    def __for_all_t(self, f, model):
        return [model.eval(f(t)) for t in range(self.total_time)]

    def eval_to_str(self, model: ModelRef):
        return """
        \r      \t {}
        \r hist:\t {}
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
            self.__for_all_t(self.arr, model),
            self.__for_all_t(self.cap, model),
            self.deqs.eval(model),
            self.__for_all_t(self.enq, model),
            self.__for_all_t(self.cenq, model),
            self.__for_all_t(self.cdeq, model),
            self.__for_all_t(self.blog, model),
            self.__for_all_t(self.head, model)
        )
