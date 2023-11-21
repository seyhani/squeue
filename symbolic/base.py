from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from typing import List, Tuple

from z3 import ExprRef, ModelRef


@dataclass
class LabeledExpr:
    expr: ExprRef
    label: str


class SymbolicStructure(ABC):
    name: str

    def __init__(self, name: str, **kwargs):
        self.name = name

    @abstractmethod
    def constrs(self) -> List[LabeledExpr]:
        pass

    @abstractmethod
    def eval(self, model: ModelRef):
        pass

    def eval_to_str(self, model: ModelRef) -> str:
        return str(self.eval(model))


class TimeIndexedStructure(SymbolicStructure, ABC):
    total_time: int

    def __init__(self, total_time, **kwargs):
        super().__init__(**kwargs)
        self.total_time = total_time

    def last_t(self):
        return self.total_time - 1
