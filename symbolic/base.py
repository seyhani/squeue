from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Callable

from z3 import ExprRef, ModelRef, ArithRef

from utils.logger import Logger


class LabeledExpr:
    expr: ExprRef
    label: str

    def __init__(self, expr: ExprRef, label: str = None):
        self.expr = expr
        if label is None:
            label = str(expr)
            Logger.warn("Using implicit label for constr: {}".format(str(expr)))
        self.label = label


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

    def eval_timed_metric(self, metric: Callable[[int], ArithRef], m: ModelRef) -> List[int]:
        return [m.eval(metric(t)) for t in range(self.total_time)]
