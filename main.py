from hist import PacketHistory
from scheduler import RoundRobinScheduler
from tiq import TimeIndexedQueue


def main():
    h = [0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
    q = TimeIndexedQueue(3, h)
    print(q)
    q.dequeue(7, 1)
    print(q)


if __name__ == '__main__':
    main()
