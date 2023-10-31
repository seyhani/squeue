from typing import List

from z3 import If, ExprRef, Int, ArithRef, IntVal

ZERO = IntVal(0)


def min_expr(a: ExprRef, b: ExprRef) -> ExprRef:
    return If(a <= b, a, b)


def find_idx_expr(arr: List[ExprRef], match: ExprRef) -> ExprRef:
    if len(arr) == 0:
        return IntVal(-1)
    last_index = len(arr) - 1
    return If(arr[last_index] == match, last_index, find_idx_expr(arr[:last_index], match))


def gte(rhs: ExprRef):
    def _gte(lhs: ExprRef):
        return lhs >= rhs

    return _gte

def lte(rhs: ExprRef):
    def _lte(lhs: ExprRef):
        return lhs <= rhs

    return _lte


def eq(rhs: ExprRef):
    def _eq(lhs: ExprRef):
        return lhs == rhs

    return _eq


def memoize(func):
    mem = {}
    if func not in mem:
        mem[func] = {}

    def _memoize(self, *args):
        if self not in mem[func]:
            mem[func][self] = {}
        if args in mem[func][self]:
            return mem[func][self][args]
        res = func(self, *args)
        mem[func][self][args] = res
        return res

    return _memoize
