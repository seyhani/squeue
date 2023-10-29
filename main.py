import time

from z3 import simplify, solve, Solver, Array, Int, IntSort, Ints, Store, Bool, And

from mem_semt_queue import MemSmtQueue
from smt_queue import IntList, SmtQueue
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
    h1 = [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0]
    q = TimeIndexedQueue(3, h1)
    q.dequeue(7, 3)
    q.dequeue(10, 1)
    print(q)
    print(q.elems_hist())


def t3():
    h1 = IntList("h1", 10)
    q = MemSmtQueue("q1", h1)
    s = Solver()
    s.add(h1.get_constrs())
    s.add(q.get_constrs())
    s.add(h1[1] == 1)
    s.add(h1[2] == 1)
    s.add(h1[3] == 1)
    s.add(h1[5] == 1)
    print(s.check())
    m = s.model()
    w = Watch()
    print(q.get_str(m))
    w.lap()


def main():
    t3()


if __name__ == '__main__':
    main()
