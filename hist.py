from typing import List, Tuple

Packet = Tuple[int, int]

Time = int
Idx = int


class Queue:
    __history: List[Packet]
    __deqs: List[Time]
    __cap: int

    def __init__(self, total_time: Time, cap: Time, hist: List[Packet]):
        self.__hist = hist
        self.__deqs = [0] * total_time
        self.__cap = cap

    def arrival(self, t: Time) -> List[Packet]:
        return list(filter(lambda p: p[0] == t, self.__hist))

    def start(self, t: Time) -> Idx:
        return next(i for i, p in enumerate(self.__hist) if p[0] == t)

    def end(self, t: Time) -> Idx:
        return len(self.__hist) - 1 - next(i for i, p in enumerate(reversed(self.__hist)) if p[0] == t)

    def enqs(self, t: Time) -> int:
        return self.end(t) - self.start(t) + 1

    def remain(self, t: Time) -> int:
        if t == 0:
            return 0
        return self.size(t - 1) - self.__deqs[t - 1]

    def acc(self, t: Time) -> int:
        if t == 0:
            return 0
        return min(self.enqs(t), self.__cap - self.remain(t))

    def size(self, t: Time) -> int:
        if t == 0:
            return 0
        return self.remain(t) + self.acc(t)

    def dequeue(self, t: Time, count: int):
        self.__deqs[t] = count
