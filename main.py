from z3 import *
from hist import Queue


def main():
    q = Queue(10, 3, [(2, 1), (2, 2), (4, 1), (4, 2), (7, 1), (7, 2)])
    q.dequeue(5, 1)
    print(q.head(6))


if __name__ == '__main__':
    main()
