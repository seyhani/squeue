from typing import List

Payload = int

NullPacket = 0


class TimeIndexedQueue:
    hist: List[Payload]
    deqs: List[int]
    cap: int

    def __init__(self, cap, hist):
        self.cap = cap
        self.hist = hist
        self.deqs = [0] * len(self.hist)
        self.enqs = [0] * len(self.hist)

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

    def head(self, t):
        if t == 0:
            return 0
        return min(list(filter(lambda i: self.cenq(i) > self.cdeq(t - 1), [i for i in range(len(self.hist))])))

    def __for_all_t(self, f):
        return [f(t) for t in range(len(self.hist))]

    def __repr__(self):
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
            [i for i in range(len(self.hist))],
            self.hist,
            self.deqs,
            self.__for_all_t(self.enq),
            self.__for_all_t(self.cenq),
            self.__for_all_t(self.cdeq),
            self.__for_all_t(self.backlog),
            self.__for_all_t(self.head)
        )
