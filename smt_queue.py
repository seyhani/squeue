from typing import List

from z3 import Int, If, IntVal

QUEUE_CAP = 3
TOTAL_TIME = 10
ZERO = IntVal(0)


class IntList:
    def __init__(self, name, size):
        self.name = name
        self.exprs = []
        for i in range(size):
            expr = Int("{}[{}]".format(name, i))
            self.exprs.append(expr)

    def __getitem__(self, i):
        return self.exprs[i]

    def get_constrs(self):
        return list(map(lambda x: x >= 0, self.exprs))

    def get_str(self, model):
        return list(map(lambda x: model[x], self.exprs))


def min_expr(a, b):
    return If(a <= b, a, b)


class SmtQueue:
    def __init__(self, name, hist):
        self.hist = hist
        self.deqs = IntList("{}_deqs".format(name), TOTAL_TIME)

    def arr(self, t):
        return If(self.hist[t] > 0, True, False)

    def cdeq(self, t):
        if t == 0:
            return ZERO
        return self.cdeq(t - 1) + self.deqs[t]

    def enq(self, t):
        return min_expr(self.arr(t), QUEUE_CAP - (self.blog(t) - self.deqs[t]))

    def cenq(self, t):
        if t == 0:
            return ZERO
        return self.cenq(t - 1) + self.enq(t)

    def blog(self, t):
        if t == 0:
            return ZERO
        return self.blog(t - 1) - self.deqs[t - 1] + self.enq(t - 1)

    def get_constrs(self):
        return list(map(lambda x: x >= 0, self.deqs))

    def __for_all_t(self, f, model):
        return [model.eval(f(t)) for t in range(TOTAL_TIME)]

    def get_str(self, model):
        return """
        \r      \t {}
        \r hist:\t {}
        \r  deq:\t {}
        \r  enq:\t {}
        \r cenq:\t {}
        \r cdeq:\t {}
        \r blog:\t {}
        """.format(
            [t for t in range(TOTAL_TIME)],
            self.hist.get_str(model),
            self.deqs.get_str(model),
            self.__for_all_t(self.enq, model),
            self.__for_all_t(self.cenq, model),
            self.__for_all_t(self.cdeq, model),
            self.__for_all_t(self.blog, model)
        )
