from hist import PacketHistory
from nqueue import PacketQueue
from scheduler import RoundRobinScheduler


def main():
    h1 = PacketHistory(10, [(2, 11), (2, 12), (4, 13), (4, 14), (4, 15), (6, 16)])
    h2 = PacketHistory(10, [(2, 21), (2, 22), (4, 23), (4, 24), (7, 25), (7, 26)])
    rr = RoundRobinScheduler(h1, h2)
    rr.run()
    print(rr.out.packets())


if __name__ == '__main__':
    main()
