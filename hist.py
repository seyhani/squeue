from typing import List, Tuple

Packet = Tuple[int, int]

Time = int
Idx = int


class Queue:
    __history: List[Packet]
    __deqs: List[Time]
    __cap: int
    __max_t: Time

    def __init__(self, max_t: Time, cap: Time, hist: List[Packet]):
        self.__hist = hist
        self.__deqs = [0] * max_t
        self.__cap = cap
        self.__max_t = max_t

    def arrival(self, t: Time) -> List[Packet]:
        return list(filter(lambda p: p[0] == t, self.__hist))

    def no_arrival(self, t: Time) -> bool:
        return len(self.arrival(t)) == 0

    def start(self, t: Time) -> Idx:
        return next(i for i, p in enumerate(self.__hist) if p[0] == t)

    def end(self, t: Time) -> Idx:
        return len(self.__hist) - 1 - next(i for i, p in enumerate(reversed(self.__hist)) if p[0] == t)

    def enqs(self, t: Time) -> int:
        if self.no_arrival(t):
            return 0
        return max(0, self.end(t) - self.start(t) + 1)

    def remain(self, t: Time) -> int:
        if t == 0:
            return 0
        return self.size(t - 1) - self.__deqs[t - 1]

    def acc(self, t: Time) -> int:
        if t == 0:
            return 0
        return min(self.enqs(t), self.__cap - self.remain(t))

    def dropped(self, t: Time) -> int:
        if t == 0:
            return 0
        return self.enqs(t) - self.acc(t)

    def size(self, t: Time) -> int:
        if t == 0:
            return 0
        return self.remain(t) + self.acc(t)

    def last(self, t: Time) -> Idx:
        return self.start(t) + self.acc(t) - 1

    def dequeue(self, t: Time, count: int):
        self.__deqs[t] = count

    def cacc(self, t: Time):
        return sum([self.acc(i) for i in range(t + 1)])

    def cdeq(self, t: Time):
        return sum(self.__deqs[0:t + 1])

    def order(self, i: Idx) -> int:
        if i == 0:
            return 0
        if i <= self.last(self.__hist[i][0]):
            return self.order(i - 1) + 1
        else:
            return self.order(i - 1)

    def head(self, t):
        return next(i for i, p in enumerate(self.__hist) if self.order(i) == self.cdeq(t - 1))
