from typing import List, Callable

from z3 import Array, IntSort, ModelRef, ExprRef, IntVal, ArrayRef, BoolSort

from symbolic.base import SymbolicStructure
from symbolic.util import eq


class SymbolicArray(SymbolicStructure):
    size: int
    __constrs: List[ExprRef]

    def __init__(self, name, size, sort):
        super().__init__(name)
        self.size = size
        self.arr = Array(name, sort, sort)
        self.__constrs = []

    def __getitem__(self, i: int) -> ArrayRef:
        return self.arr[i]

    def add_constr(self, i: int, expr_producer: Callable[[ArrayRef], ExprRef]):
        self.__constrs.append(expr_producer(self[i]))

    def constrs(self) -> List[ExprRef]:
        return self.__constrs

    def eval(self, model: ModelRef):
        return [model.eval(self.arr[t]) for t in range(self.size)]


class BoolArray(SymbolicArray):
    def __init__(self, name, size):
        super().__init__(name, size, BoolSort())

    def eval(self, model: ModelRef) -> List[bool]:
        return super().eval(model)


class IntArray(SymbolicArray):
    def __init__(self, name, size):
        super().__init__(name, size, IntSort())

    def eval(self, model: ModelRef) -> List[int]:
        return super().eval(model)

    @staticmethod
    def create(name: str, ints: List[int]):
        int_array = IntArray(name, len(ints))
        for i, v in enumerate(ints):
            int_array.add_constr(i, eq(IntVal(v)))
        return int_array
