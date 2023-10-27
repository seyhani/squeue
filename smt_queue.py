from typing import List, Tuple

Packet = Tuple[int, int]

Time = int
Idx = int


class SmtQueue:
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

