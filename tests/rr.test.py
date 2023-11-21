from symbolic.hist import SymbolicHistory
from schedulers.rr import RoundRobinScheduler
from symbolic.test_util import instantiate


def test_rr():
    h0 = SymbolicHistory.create("h0", [0, 10, 0, 0, 20, 0, 0])
    h1 = SymbolicHistory.create("h1", [0, 0, 0, 0, 11, 0, 0])
    h2 = SymbolicHistory.create("h2", [0, 0, 0, 12, 22, 0, 0])
    rr = RoundRobinScheduler("rr", 3, [h0, h1, h2])
    rr.run()
    c, s = instantiate(rr)
    assert c[2] == 10
    assert c[4] == 12
    assert c[5] == 20
    assert c[6] == 11


def main():
    test_rr()


if __name__ == '__main__':
    main()
