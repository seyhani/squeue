from typing import List, Callable

from z3 import Array, IntSort, ModelRef, ExprRef, IntVal, ArrayRef

from symbolic.base import SymbolicStructure
from symbolic.util import eq


class BoolArray(SymbolicStructure):
    size: int

    def constrs(self) -> List[ExprRef]:
        pass

    def eval(self, model: ModelRef):
        pass


class IntArray(SymbolicStructure):
    size: int
    __constrs: List[ExprRef]

    def __init__(self, name, size):
        super().__init__(name)
        self.size = size
        self.arr = Array(name, IntSort(), IntSort())
        self.__constrs = []

    def __getitem__(self, i: int) -> ArrayRef:
        return self.arr[i]

    def add_constr(self, i: int, expr_producer: Callable[[ArrayRef], ExprRef]):
        self.__constrs.append(expr_producer(self[i]))

    def constrs(self) -> List[ExprRef]:
        return self.__constrs

    def eval(self, model: ModelRef) -> List[int]:
        return [model.eval(self.arr[t]) for t in range(self.size)]

    @staticmethod
    def create(name: str, ints: List[int]):
        int_array = IntArray(name, len(ints))
        for i, v in enumerate(ints):
            int_array.add_constr(i, eq(IntVal(v)))
        return int_array
