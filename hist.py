from typing import List, Tuple

Packet = Tuple[int, int]


class Queue:
    __history: List[Packet]
    __deqs: List[int]
    __tails: List[int]

    def __init__(self, total_time: int, hist: List[Packet]):
        self.__hist = hist
        self.__deqs = [0] * total_time
        self.__tails = [-1] * total_time

    def dequeue(self, t: int, count: int):
        self.__deqs[t] = count

    def cdeq(self, t: int):
        return sum(self.__deqs[0:t + 1])
