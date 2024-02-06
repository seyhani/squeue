from typing import List

from z3 import IntVal, If, Or, ModelRef

from symbolic.arr import IntArray
from symbolic.base import TimeIndexedStructure, LabeledExpr
from symbolic.util import ZERO, memoize, max_expr, min_expr, MAX_VAL


class SymbolicHistory(IntArray, TimeIndexedStructure):
    def __init__(self, name, total_time):
        super().__init__(name=name, total_time=total_time, size=total_time)
        self.add_constr(LabeledExpr(self[0] == 0, "{}[{}] == {}".format(self.name, 0, 0)))
        for t in range(self.total_time):
            self.add_constr(LabeledExpr(self[t] >= ZERO, "{}[{}] >= {}".format(self.name, t, 0)))

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
            self.eval_timed_metric(self.cc, model),
            self.eval_timed_metric(self.czero, model),
            self.eval_timed_metric(self.ming, model),
            self.eval_timed_metric(self.maxg, model)
        )


def create_hist(name: str, ints: List[int], total_time=None):
    if total_time is None:
        total_time = len(ints)
    hist = SymbolicHistory(name=name, total_time=total_time)
    for t in range(1, total_time):
        v = 0
        if t <= len(ints):
            v = IntVal(ints[t - 1])
        hist.add_constr(LabeledExpr(hist[t] == v, "{}[{}] = {}".format(hist.name, t, v)))
    return hist


def single_id_hist(name: str, total_time: int, idx: int):
    hist = SymbolicHistory(name, total_time)
    for t in range(total_time):
        hist.add_constr(LabeledExpr(Or(hist[t] == 0, hist[t] == idx), "{}[{}] = {}|{}".format(hist.name, t, 0, idx)))
    return hist


def multiple_id_hist(name: str, total_time: int, ids: List[int]):
    hist = SymbolicHistory(name, total_time)
    for t in range(total_time):
        hist.add_constr(LabeledExpr(
            Or(hist[t] == 0, Or([hist[t] == idx for idx in ids])), "{}[{}] = {}|{}".format(hist.name, t, 0, ids)))
    return hist


def non_trivial_hist(name: str, total_time: int, idx: int):
    hist = single_id_hist(name, total_time, idx)
    hist.add_constr(LabeledExpr(hist.cc(1) > 0, "{}::cc({}) > {}".format(hist.name, 1, 0)))
    hist.add_constr(LabeledExpr(hist.cc() > 1, "{}::cc() > {}".format(hist.name, 1)))
    return hist
