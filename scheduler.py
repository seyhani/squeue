from typing import List

from hist import PacketHistory
from nqueue import PacketQueue


class RoundRobinScheduler:
    queues: List[PacketQueue]
    out: PacketHistory

    def __init__(self, h1: PacketHistory, h2: PacketHistory):
        self.queues = []
        self.queues.append(PacketQueue(5, h1))
        self.queues.append(PacketQueue(5, h2))
        self.out = PacketHistory(10, [])

    def run(self):
        last_q = 0
        for t in range(1, 10):
            for i in range(len(self.queues)):
                ci = (last_q + i) % len(self.queues)
                q = self.queues[ci]
                if not q.empty(t):
                    p = q.head_packet(t)
                    q.dequeue(t, 1)
                    self.out.push((t, p[1]))
                    last_q = i
                    break
