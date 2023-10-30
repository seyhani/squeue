import time

from z3 import simplify, solve, Solver, Array, Int, IntSort, Ints, Store, Bool, And

from mem_semt_queue import MemSmtQueue
from simple_scheduler import SimpleScheduler
from smt_queue import IntList, SmtQueue, TOTAL_TIME
from smt_scheduler import SmtRoundRobinScheduler
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
    q.dequeue(7, 2)
    q.dequeue(8, 1)
    print(q)
    print(q.elems_hist())
    print(q.head_pkt(12))


def t3():
    h1 = IntList("h1", [11, 12, 0, 0, 15])
    ho = IntList("ho")
    q = MemSmtQueue("q1", h1)
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
    h1 = IntList("h1", [0, 0, 12, 13, 14, 15, 0, 0, 0, 0])
    h2 = IntList("h2", [0, 0, 22, 23, 24, 0, 0, 0, 0, 0])
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


def main():
    t4()


if __name__ == '__main__':
    main()
