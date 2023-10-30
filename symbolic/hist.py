from symbolic.arr import IntArray
from symbolic.base import ZERO


class SymbolicHistory(IntArray):
    def __init__(self, name, size):
        super().__init__(name, size)
        self[0] = ZERO
