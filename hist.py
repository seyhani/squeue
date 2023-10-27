from typing import List, Tuple

Packet = Tuple[int, int]
Time = int


class PacketHistory:
    __hist: List[Packet]
    __max_t: Time

    def __init__(self, max_t, hist: List[Packet]):
        if not PacketHistory.__non_decreasing_time(hist):
            raise RuntimeError("Non decreasing packet timestamps")

        if len(hist) > 0 and max([p[0] for p in hist]) > max_t:
            raise RuntimeError("Max timestamp greater than: " + str(max_t))

        self.__hist = hist
        self.__max_t = max_t

    def push(self, p: Packet):
        self.__hist.append(p)

    def size(self):
        return len(self.__hist)

    def packets(self):
        return self.__hist

    def max_t(self):
        return self.__max_t

    def __getitem__(self, idx):
        return self.__hist[idx]

    @staticmethod
    def __non_decreasing_time(hist: List[Packet]):
        timestamps = [p[0] for p in hist]
        return all(t1 <= t2 for t1, t2 in zip(timestamps, timestamps[1:]))
