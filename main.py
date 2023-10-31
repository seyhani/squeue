import time

from z3 import Solver

from symbolic.mem_smt_queue import MemSymbolicQueue
from symbolic.queue import IntArray, TOTAL_TIME
from symbolic.rr import SmtRoundRobinScheduler
from tiq import TimeIndexedQueue


class Watch:
    def __init__(self):
        self.last = time.time()

    def lap(self):
        now = time.time()
        print(now - self.last)
        self.last = now


def t1():
    h1 = [0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0]
    q = TimeIndexedQueue(3, h1)
    q.dequeue(7, 1)
    q.dequeue(10, 1)
    print(q)


def t2():
    h1 = [0, 11, 12, 13, 0, 0, 0, 0, 0, 0, 101, 111, 0, 0, 0]
    q = TimeIndexedQueue(3, h1)
    q.dequeue(5, 1)
    print(q)
    print(q.head_pkt(4))
    print(q.head_pkt(5))
    print(q.head_pkt(6))
    # print(q.elems_hist())
    # print(q.head_pkt(12))


def t3():
    h1 = IntArray("h1", [11, 12, 0, 0, 15])
    ho = IntArray("ho")
    q = MemSymbolicQueue("q1", h1)
    s = Solver()
    q.set_deqs({5: 1})
    s.add(q.constrs)
    s.add(ho.constrs)
    s.add(ho[1] == q.head_pkt(5))
    # s.add(h1[2] == 3)
    # s.add(h1[3] == 4)
    s.check()
    m = s.model()
    print(m.eval(q.head_pkt(5)))
    print(m.eval(q.head_pkt(6)))
    print(ho.get_str(m))

    # q = MemSmtQueue("q1", h1)
    # s = Solver()
    # s.add(h1.get_constrs())
    # s.add(q.get_constrs())
    # s.add(h1[1] == 11)
    # s.add(h1[2] == 12)
    # s.add(h1[3] == 13)
    # s.add(h1[5] == 15)
    # s.add(q.head(5) == 2)
    # s.check()
    # m = s.model()
    # print(q.get_str(m))
    # print(m.eval(q.tail(6, 0)))


def t4():
    h1 = IntArray("h1", [0, 0, 12, 13, 14, 15, 0, 0, 0, 0])
    h2 = IntArray("h2", [0, 0, 22, 23, 24, 0, 0, 0, 0, 0])
    rr = SmtRoundRobinScheduler(h1, h2)
    rr.run()
    s = Solver()
    constrs = rr.constrs
    s.add(constrs)
    print(s.check())
    m = s.model()
    print("h1: ", h1.get_str(m))
    print("h2: ", h2.get_str(m))
    print("ho: ", rr.out.get_str(m))
    print("ls: ", rr.last_served.get_str(m))
    print(rr.queues[0].get_str(m))
    print(rr.queues[0].get_str(m))


def for_all_t(f):
    return [f(t) for t in range(1, TOTAL_TIME)]


def exists_t(f):
    return []


def rr_test():
    h11 = IntArray("h11")
    h12 = IntArray("h12")
    h21 = IntArray("h21")
    h22 = IntArray("h22")
    rr = SmtRoundRobinScheduler(h11, h12, h21, h22)
    constrs = []
    constrs.extend(for_all_t(lambda t: h11.ccount(t) + h12.ccount(t) > t))
    constrs.extend(for_all_t(lambda t: h21.ccount(t) + h22.ccount(t) > t))

    query = []

    h1_pkt_count = lambda t: rr.out.ccount(t, lambda p: p / 10 < 2)
    h2_pkt_count = lambda t: rr.out.ccount(t, lambda p: p / 10 > 1)

    query.extend(exists_t(lambda t: h1_pkt_count(t) - h2_pkt_count(t) >= 4))


def main():
    t4()


if __name__ == '__main__':
    main()
