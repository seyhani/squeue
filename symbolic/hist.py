from z3 import IntSort

from symbolic.arr import IntArray
from symbolic.base import TimeIndexedStructure
from symbolic.util import gte, ZERO, eq


class SymbolicHistory(IntArray, TimeIndexedStructure):
    def __init__(self, name, total_time):
        super().__init__(name=name, total_time=total_time, size=total_time)
        self.add_constr(0, eq(ZERO))
        for t in range(self.total_time):
            self.add_constr(t, gte(ZERO))
