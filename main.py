from hist import PacketHistory
from nqueue import Queue


def main():
    h1 = PacketHistory(10, [(2, 1), (2, 2), (4, 1), (4, 2), (7, 1), (7, 2)])
    q1 = Queue(3, h1)
    # q1 = Queue(10, 3, [(2, 1), (2, 2), (4, 1), (4, 2), (7, 1), (7, 2)])
    # q2 = Queue(10, 3, [(2, 1), (2, 2), (4, 1), (4, 2), (7, 1), (7, 2)])
    print(q1.head(6))
    q1.dequeue(5, 1)
    print(q1.head(6))


if __name__ == '__main__':
    main()
