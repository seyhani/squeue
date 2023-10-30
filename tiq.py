from typing import List


class TimeIndexedQueue:
    hist: List[int]
    deqs: List[int]
    cap: int

    def __init__(self, cap, hist):
        self.cap = cap
        self.hist = hist
        self.deqs = [0] * len(self.hist)

    def dequeue(self, t, count):
        self.deqs[t] = count

    def cdeq(self, t):
        if t == 0:
            return 0
        return self.cdeq(t - 1) + self.deqs[t]

    def arr(self, t):
        if self.hist[t] > 0:
            return 1
        return 0

    def enq(self, t):
        return min(self.arr(t), self.cap - (self.backlog(t) - self.deqs[t]))

    def cenq(self, t):
        if t == 0:
            return 0
        return self.cenq(t - 1) + self.enq(t)

    def backlog(self, t):
        if t == 0:
            return 0
        return self.backlog(t - 1) - self.deqs[t - 1] + self.enq(t - 1)

    def tail(self, t, i):
        if t == 0 or i > self.backlog(t) or self.backlog(t) == 0:
            return 0
        if self.enq(t - 1) == 1:
            if i == 0:
                return t - 1
            return self.tail(t - 1, i - 1)
        else:
            return self.tail(t - 1, i)

    def head_pkt(self, t):
        if t == 0:
            return 0
        return self.hist[self.tail(t, self.backlog(t) - 1)]

    def elems(self, t):
        return list(reversed(list(filter(lambda p: p > 0, [self.tail(t, i) for i in range(self.backlog(t))]))))

    def __for_all_t(self, f):
        return [f(t) for t in range(len(self.hist))]

    def elems_hist(self):
        return "".join(["\rt = {}:\t{}\n".format(t, self.elems(t)) for t in range(len(self.hist))])

    def __repr__(self):
        return """
        \r      \t {}
        \r hist:\t {}
        \r  enq:\t {}
        \r blog:\t {}
        \r  deq:\t {}
        \r   h0:\t {}
        \r   h1:\t {}
        \r   h2:\t {}
        """.format(
            [i % 10 for i in range(len(self.hist))],
            self.hist,
            self.__for_all_t(self.enq),
            self.__for_all_t(self.backlog),
            self.deqs,
            self.__for_all_t(lambda t: self.tail(t, 0)),
            self.__for_all_t(lambda t: self.tail(t, 1)),
            self.__for_all_t(lambda t: self.tail(t, 2))
        )
