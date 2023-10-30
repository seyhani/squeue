from mem_semt_queue import MemSmtQueue
from smt_queue import SmtQueue, IntList, TOTAL_TIME


class SimpleScheduler:
    queue: SmtQueue
    out: IntList

    def __init__(self, h1):
        self.queue = MemSmtQueue("q1", h1)
        self.out = IntList("qo")
        self.constrs = []
        self.constrs.extend(self.queue.constrs)
        self.constrs.extend(self.out)

    def run(self):
        constrs = []
        for t in range(1, TOTAL_TIME):
            constrs.append(self.out[self.queue.tail(4, 0)] == self.queue.hist[3])
        self.constrs.extend(constrs)
