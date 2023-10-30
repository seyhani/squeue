from typing import List, Dict

from z3 import Int, If, IntVal, Or, IntSort, Array

QUEUE_CAP = 3
TOTAL_TIME = 10
ZERO = IntVal(0)


class IntList:
    def __init__(self, name, hist=[]):
        self.name = name
        self.arr = Array(name, IntSort(), IntSort())
        self.constrs = [self.arr[t] >= 0 for t in range(TOTAL_TIME)]
        for i, h in enumerate(hist):
            self.constrs.append(self.arr[i] == hist[i])

    def __getitem__(self, i):
        return self.arr[i]

    def get_str(self, model):
        return [model.eval(self.arr[t]) for t in range(TOTAL_TIME)]


def min_expr(a, b):
    return If(a <= b, a, b)


class SmtQueue:
    def __init__(self, name, hist: IntList):
        self.hist = hist
        self.deqs = IntList("{}_deqs".format(name))
        self.constrs = []
        self.constrs.extend(self.hist.constrs)
        self.constrs.extend(self.deqs.constrs)
        self.constrs.append(self.deqs[0] == 0)

    def set_deqs(self, deqs: Dict[int, int]):
        for t in range(TOTAL_TIME):
            self.constrs.append(self.deqs[t] == deqs.get(t, 0))

    def arr(self, t):
        return If(self.hist[t] > 0, True, False)

    def cdeq(self, t):
        if t == 0:
            return self.deqs[0]
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

    def tail(self, t, i):
        if t == 0:
            return ZERO
        return If(Or(i > self.blog(t), self.blog(t) == ZERO),
                  ZERO,
                  If(self.enq(t - 1) == 1,
                     If(i == 0,
                        IntVal(t - 1),
                        self.tail(t - 1, i - 1)
                        ),
                     self.tail(t - 1, i))
                  )

    def head(self, t):
        return self.tail(t, self.blog(t) - 1)

    def head_pkt(self, t):
        return self.hist[self.head(t)]

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
        \r head:\t {}
        """.format(
            [t for t in range(TOTAL_TIME)],
            self.hist.get_str(model),
            self.deqs.get_str(model),
            self.__for_all_t(self.enq, model),
            self.__for_all_t(self.cenq, model),
            self.__for_all_t(self.cdeq, model),
            self.__for_all_t(self.blog, model),
            self.__for_all_t(self.head, model)
        )
