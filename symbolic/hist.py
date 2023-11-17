from typing import List

from z3 import IntVal, If, Or, And

from symbolic.arr import IntArray
from symbolic.base import TimeIndexedStructure
from symbolic.util import gte, ZERO, eq, memoize, max_expr, min_expr, MAX_VAL, forall


class SymbolicHistory(IntArray, TimeIndexedStructure):
    def __init__(self, name, total_time):
        super().__init__(name=name, total_time=total_time, size=total_time)
        self.add_constr(0, eq(ZERO))
        for t in range(self.total_time):
            self.add_constr(t, gte(ZERO))

    @memoize
    def ccount(self, t: int, id: int = 0):
        res = IntVal(0)
        for i in range(1, t):
            res += If(If(id == 0, self[i] > 0, self[i] == id), 1, 0)
        return res

    @memoize
    def czero(self, t):
        if t == 0:
            return ZERO
        return If(self[t] == 0, self.czero(t - 1) + 1, ZERO)

    @memoize
    def min_gap(self, t):
        if t == 0:
            return MAX_VAL
        return If(self.ccount(t) < 2, MAX_VAL,
                  If(self[t] > 0, min_expr(self.czero(t - 1), self.min_gap(t - 1)), self.min_gap(t - 1)))


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


def single_id_hist(name: str, total_time: int, id: int):
    h = SymbolicHistory(name, total_time)
    for t in range(total_time):
        h.add_constr(t, lambda ht: Or(ht == 0, ht == id))
    return h
