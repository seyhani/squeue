from z3 import *
from hist import Queue


def main():
    q = Queue(5, [(1, 0), (1, 0), (1, 0), (2, 0), (2, 0), (3, 0), (3, 0), (4, 0), (4, 0)])
    q.dequeue(0, 1)
    q.dequeue(1, 1)
    q.dequeue(2, 1)
    print(q.cdeq(0))


if __name__ == '__main__':
    main()
