from z3 import simplify, solve, Solver, Array, Int, IntSort, Ints, Store

from smt_queue import IntList, SmtQueue
from tiq import TimeIndexedQueue


def t1():
    h1 = [0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0]
    q = TimeIndexedQueue(3, h1)
    q.dequeue(7, 1)
    q.dequeue(10, 1)
    print(q)


def t2():
    #    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4]
    h1 = [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0]
    q = TimeIndexedQueue(3, h1)
    q.dequeue(7, 3)
    q.dequeue(10, 1)
    print(q)
    print(q.elems_hist())


def main():
    t2()


if __name__ == '__main__':
    main()
