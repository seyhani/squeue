from typing import List

from hist import PacketHistory, Time, Packet
from nqueue import Idx


class SmtQueue:
    __hist: PacketHistory
    __deqs: List[Time]
    __cap: int

    def __init__(self, cap: int, hist: PacketHistory):
        self.__hist = hist
        self.__deqs = [0] * hist.max_t()
        self.__cap = cap

    def start(self, t: Time) -> Idx:
        return next(i for i, p in enumerate(self.__hist) if p[0] == t)
