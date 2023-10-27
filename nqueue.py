from typing import List, Tuple

from hist import Packet, Time, PacketHistory

Idx = int


class PacketQueue:
    __hist: PacketHistory
    __deqs: List[Time]
    __cap: int

    def __init__(self, cap: int, hist: PacketHistory):
        self.__hist = hist
        self.__deqs = [0] * hist.max_t()
        self.__cap = cap

    def arrival(self, t: Time) -> List[Packet]:
        return list(filter(lambda p: p[0] == t, self.__hist.packets()))

    def no_arrival(self, t: Time) -> bool:
        return len(self.arrival(t)) == 0

    def start(self, t: Time) -> Idx:
        return next(i for i, p in enumerate(self.__hist) if p[0] == t)

    def end(self, t: Time) -> Idx:
        return self.__hist.size() - 1 - next(i for i, p in enumerate(reversed(self.__hist.packets())) if p[0] == t)

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

    def orders(self):
        return [self.order(i) for i, p in enumerate(self.__hist)]

    def empty(self, t):
        return self.cdeq(t - 1) >= self.cacc(t)

    def head(self, t):
        return next(i for i, p in enumerate(self.__hist) if self.order(i) == self.cdeq(t - 1))

    def head_packet(self, t):
        return self.__hist[self.head(t)]
