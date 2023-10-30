from typing import List, Dict

from z3 import Array, IntSort, ModelRef, ExprRef, IntVal, ArrayRef

from symbolic.base import SymbolicStructure


class IntArray(SymbolicStructure):
    size: int
    __constrs: List[ExprRef]

    def __init__(self, name, size):
        super().__init__(name)
        self.size = size
        self.arr = Array(name, IntSort(), IntSort())
        self.__constrs = []
        for i in range(size):
            self.__constrs.append(self.arr[i] >= 0)

    def __getitem__(self, i) -> ArrayRef:
        return self.arr[i]

    def __setitem__(self, i, v: ExprRef):
        self.__constrs.append(self[i] == v)

    def constrs(self) -> List[ExprRef]:
        return self.__constrs

    def eval(self, model: ModelRef) -> List[int]:
        return [model.eval(self.arr[t]) for t in range(self.size)]

    @staticmethod
    def create(name: str, ints: List[int]):
        int_array = IntArray(name, len(ints))
        for i, v in enumerate(ints):
            int_array[i] = IntVal(v)
        return int_array
