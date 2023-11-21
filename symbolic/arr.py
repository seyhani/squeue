from typing import List, Callable

from z3 import Array, IntSort, ModelRef, ExprRef, IntVal, ArrayRef, BoolSort, ArithRef

from symbolic.base import SymbolicStructure
from symbolic.util import eq


class SymbolicArray(SymbolicStructure):
    size: int
    __constrs: List[ExprRef]

    def __init__(self, name, size, sort, **kwargs):
        super().__init__(name=name, **kwargs)
        self.size = size
        self.arr = Array(name, IntSort(), sort)
        self.__constrs = []

    def __getitem__(self, i: int) -> ArithRef:
        return self.arr[i]

    def add_constr(self, i: int, expr_producer: Callable[[ArrayRef], ExprRef]):
        self.__constrs.append(expr_producer(self[i]))

    def add_constr_expr(self, expr: ExprRef):
        self.__constrs.append(expr)

    def constrs(self) -> List[ExprRef]:
        return self.__constrs

    def eval(self, model: ModelRef):
        return [model.eval(self[t]) for t in range(self.size)]


class BoolArray(SymbolicArray):
    def __init__(self, name, size):
        super().__init__(name, size, BoolSort())

    def eval(self, model: ModelRef) -> List[bool]:
        return super().eval(model)


class IntArray(SymbolicArray):
    def __init__(self, **kwargs):
        super().__init__(sort=IntSort(), **kwargs)

    def eval(self, model: ModelRef) -> List[int]:
        return super().eval(model)
