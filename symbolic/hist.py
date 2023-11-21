from typing import List

from z3 import IntVal, If, Or, And, BoolRef, ModelRef

from symbolic.arr import IntArray
from symbolic.base import TimeIndexedStructure
from symbolic.util import gte, ZERO, eq, memoize, max_expr, min_expr, MAX_VAL, forall


def match_id(p, idx: int = -1) -> BoolRef:
    return If(idx == -1, p > 0, p == idx)


class SymbolicHistory(IntArray, TimeIndexedStructure):
    def __init__(self, name, total_time):
        super().__init__(name=name, total_time=total_time, size=total_time)
        self.add_constr(0, eq(ZERO))
        for t in range(self.total_time):
            self.add_constr(t, gte(ZERO))

    def project(self, idx):
        if not isinstance(idx, int) or idx <= 0:
            raise RuntimeError("Projection operand must be an int > 0")

        class ProjectedHistory(SymbolicHistory):
            def __init__(self, name, total_time):
                super().__init__(name, total_time)

            def __getitem__(self, t):
                val = super(ProjectedHistory, self).__getitem__(t)
                return If(val == IntVal(idx), val, ZERO)

        return ProjectedHistory(self.name, self.total_time)

    @memoize
    def cc(self, t=None):
        if t is None:
            t = self.last_t()
        res = IntVal(0)
        for i in range(1, t + 1):
            res += If(self[i] > 0, 1, 0)
        return res

    @memoize
    def czero(self, t=None):
        if t is None:
            t = self.last_t()
        if t == 0:
            return ZERO
        return If(self[t] == 0, self.czero(t - 1) + 1, ZERO)

    @memoize
    def maxg(self, t=None):
        if t is None:
            t = self.last_t()
        if t == 0:
            return IntVal(-1)
        return If(self.cc(t) < 2, IntVal(-1),
                  If(self[t] > 0, max_expr(self.czero(t - 1), self.maxg(t - 1)), self.maxg(t - 1)))

    @memoize
    def ming(self, t=None):
        if t is None:
            t = self.last_t()
        if t == 0:
            return MAX_VAL
        return If(self.cc(t) < 2, MAX_VAL,
                  If(self[t] > 0, min_expr(self.czero(t - 1), self.ming(t - 1)), self.ming(t - 1)))

    def __or__(self, i: int):
        return self.project(i)

    def eval_to_str(self, model: ModelRef):
        return """
        \r      \t {}
        \r hist:\t {}
        \r   cc:\t {}
        \r   cz:\t {}
        \r ming:\t {}
        \r maxg:\t {}
        """.format(
            [t for t in range(self.total_time)],
            self.eval(model),
            [model.eval(self.cc(t)) for t in range(self.total_time)],
            [model.eval(self.czero(t)) for t in range(self.total_time)],
            [model.eval(self.ming(t)) for t in range(self.total_time)],
            [model.eval(self.maxg(t)) for t in range(self.total_time)],
        )


def create_hist(name: str, ints: List[int], total_time=-1):
    if total_time == -1:
        total_time = len(ints)
    hist = SymbolicHistory(name=name, total_time=total_time)
    for t in range(1, total_time):
        v = 0
        if t <= len(ints):
            v = IntVal(ints[t - 1])
        hist.add_constr(t, eq(v))
    return hist


def single_id_hist(name: str, total_time: int, idx: int):
    h = SymbolicHistory(name, total_time)
    for t in range(total_time):
        h.add_constr(t, lambda ht: Or(ht == 0, ht == idx))
    return h


def non_trivial_hist(name: str, total_time: int, idx: int):
    h = single_id_hist(name, total_time, idx)
    h.add_constr_expr(h.cc(1) > 0)
    h.add_constr_expr(h.cc() > 1)
    return h
