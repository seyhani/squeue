from z3 import If, ExprRef, Int


def min_expr(a: ExprRef, b: ExprRef) -> ExprRef:
    return If(a <= b, a, b)


def memoize(func):
    mem = {}
    if func not in mem:
        mem[func] = {}

    def _memoize(self, *args):
        if args in mem[func]:
            return mem[func][args]
        res = func(self, *args)
        mem[func][args] = res
        return res

    return _memoize
