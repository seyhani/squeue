from symbolic.arr import IntArray
from symbolic.util import gte, ZERO, eq


class SymbolicHistory(IntArray):
    def __init__(self, name, size):
        super().__init__(name, size)
        self.add_constr(0, eq(ZERO))
        for i in range(size):
            self.add_constr(i, gte(ZERO))
