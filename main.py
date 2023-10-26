from z3 import *
from hist import Queue


def main():
    q = Queue(5, 3, [(1, 1), (2, 2), (3, 3)])
    q.dequeue(1, 1)
    print("Enqs[1]: ", q.enqs(1))
    print("Rem[1]: ", q.remain(1))
    print("Acc[1]: ", q.acc(1))
    print("Size[1]: ", q.size(1))
    print("Rem[2]: ", q.remain(2))
    print("Acc[2]: ", q.acc(2))
    print("Size[2]: ", q.size(2))


if __name__ == '__main__':
    main()
