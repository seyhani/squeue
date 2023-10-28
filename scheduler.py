from typing import List

from hist import PacketHistory
from nqueue import PacketQueue


class RoundRobinScheduler:
    queues: List[PacketQueue]
    out: PacketHistory

    def __init__(self, queue_size: int, hists: List[PacketHistory]):
        self.queues = []
        for hist in hists:
            self.queues.append(PacketQueue(queue_size, hist))
        self.out = PacketHistory(hists[0].max_t(), [])

    def run(self):
        last_q = len(self.queues) - 1
        for t in range(1, self.out.max_t()):
            for i in range(len(self.queues)):
                ci = (last_q + i + 1) % len(self.queues)
                q = self.queues[ci]
                if not q.empty(t):
                    p = q.head_packet(t)
                    q.dequeue(t, 1)
                    self.out.push((t, p[1]))
                    last_q = ci
                    break
