from typing import List

from z3 import Array, IntSort, ModelRef, ArithRef

from symbolic.base import SymbolicStructure, LabeledExpr


class SymbolicArray(SymbolicStructure):
    size: int
    __constrs: List[LabeledExpr]

    def __init__(self, name, size, sort, **kwargs):
        super().__init__(name=name, **kwargs)
        self.size = size
        self.arr = Array(name, IntSort(), sort)
        self.__constrs = []

    def __getitem__(self, i: int) -> ArithRef:
        return self.arr[i]

    def add_constr(self, constr: LabeledExpr):
        self.__constrs.append(constr)

    def constrs(self) -> List[LabeledExpr]:
        return self.__constrs

    def eval(self, model: ModelRef) -> List:
        return [model.eval(self[t]) for t in range(self.size)]


class IntArray(SymbolicArray):
    def __init__(self, vals: List[int] = [], **kwargs):
        super().__init__(sort=IntSort(), **kwargs)
        for i, v in enumerate(vals):
            self.add_constr(LabeledExpr(self[i] == v, "{}[{}] = {}".format(self.name, i, v)))

    def eval(self, model: ModelRef) -> List[int]:
        return super().eval(model)
