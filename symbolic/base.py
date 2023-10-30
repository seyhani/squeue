from abc import ABC, abstractmethod
from typing import List, Dict

from z3 import ExprRef, ModelRef, IntVal

ZERO = IntVal(0)


class SymbolicStructure(ABC):
    name: str

    def __init__(self, name: str):
        self.name = name
        self.__memo = {}

    @abstractmethod
    def constrs(self) -> List[ExprRef]:
        pass

    @abstractmethod
    def eval(self, model: ModelRef):
        pass

    def eval_to_str(self, model: ModelRef) -> str:
        return str(self.eval(model))
